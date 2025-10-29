#!/usr/bin/env python3
"""
Lightweight Federal Regulatory Compliance RAG System
Single-file implementation - minimal dependencies, maximum simplicity
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter

# Try to import optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    CRAWLING_AVAILABLE = True
except ImportError:
    CRAWLING_AVAILABLE = False
    print("⚠ Install requests & beautifulsoup4 for crawling: pip install requests beautifulsoup4")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ Install openai for AI features: pip install openai")


class LightweightRAG:
    """
    Ultra-lightweight RAG system for regulatory compliance
    No vector database - uses simple keyword + TF-IDF search
    """

    def __init__(self, data_file: str = "regulatory_content.json"):
        self.data_file = data_file
        self.documents = []
        self.openai_client = None

        # Initialize OpenAI if available
        api_key = os.getenv('OPENAI_API_KEY')
        if OPENAI_AVAILABLE and api_key:
            self.openai_client = OpenAI(api_key=api_key)

    def crawl_url(self, url: str) -> Dict[str, Any]:
        """Crawl a single URL and extract text"""
        if not CRAWLING_AVAILABLE:
            return {}

        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Compliance Research Bot)'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts and styles
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url

            # Get main content
            main = soup.find('main') or soup.find('article') or soup.find('body')
            text = main.get_text(separator='\n', strip=True) if main else ''

            # Clean text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)

            return {
                'url': url,
                'title': title_text,
                'content': clean_text,
                'crawl_date': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"✗ Failed to crawl {url}: {e}")
            return {}

    def crawl_urls_from_csv(self, csv_path: str, max_urls: int = 10):
        """Crawl URLs from CSV file"""
        import csv

        print(f"Loading URLs from {csv_path}...")

        urls = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'URL' in row and row['URL']:
                    urls.append(row['URL'])

        urls = urls[:max_urls]
        print(f"Crawling {len(urls)} URLs...")

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            doc = self.crawl_url(url)
            if doc:
                self.documents.append(doc)

        print(f"✓ Crawled {len(self.documents)} documents")
        self.save_documents()

    def load_documents(self):
        """Load documents from JSON file"""
        if not os.path.exists(self.data_file):
            print(f"No data file found at {self.data_file}")
            return

        with open(self.data_file, 'r') as f:
            self.documents = json.load(f)

        print(f"✓ Loaded {len(self.documents)} documents")

    def save_documents(self):
        """Save documents to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.documents, f, indent=2)

        print(f"✓ Saved {len(self.documents)} documents to {self.data_file}")

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_len = len(word) + 1
            if current_length + word_len > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_len
            else:
                current_chunk.append(word)
                current_length += word_len

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def compute_tfidf_scores(self, query: str, text: str) -> float:
        """Simple TF-IDF scoring"""
        query_terms = query.lower().split()
        text_lower = text.lower()

        # Count term frequencies
        score = 0
        for term in query_terms:
            # Term frequency in document
            tf = text_lower.count(term)
            if tf > 0:
                # Simple scoring: more occurrences = higher score
                score += tf

        return score

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search documents using simple keyword + TF-IDF
        No vector embeddings needed
        """
        if not self.documents:
            return []

        results = []

        for doc in self.documents:
            content = doc.get('content', '')
            chunks = self.chunk_text(content, chunk_size=1000)

            for i, chunk in enumerate(chunks):
                score = self.compute_tfidf_scores(query, chunk)

                if score > 0:
                    results.append({
                        'url': doc.get('url', ''),
                        'title': doc.get('title', 'Untitled'),
                        'chunk': chunk,
                        'chunk_index': i,
                        'score': score
                    })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:top_k]

    def build_context(self, search_results: List[Dict[str, Any]], max_chars: int = 4000) -> str:
        """Build context from search results"""
        context_parts = []
        current_length = 0

        for i, result in enumerate(search_results, 1):
            chunk = result['chunk']
            title = result['title']
            url = result['url']

            part = f"[Source {i}] {title}\nURL: {url}\n\n{chunk}\n\n---\n\n"

            if current_length + len(part) > max_chars:
                break

            context_parts.append(part)
            current_length += len(part)

        return ''.join(context_parts)

    def ask(self, question: str, use_ai: bool = True) -> Dict[str, Any]:
        """Ask a question"""
        print(f"\nSearching for: {question}")

        # Search
        results = self.search(question, top_k=5)

        if not results:
            return {
                'question': question,
                'answer': 'No relevant regulatory content found.',
                'sources': []
            }

        # Build context
        context = self.build_context(results)

        # Generate answer with AI if available
        if use_ai and self.openai_client:
            answer = self.generate_ai_answer(question, context)
        else:
            answer = "Relevant sources found. Please review the sources below for details."

        # Prepare sources
        sources = [
            {
                'title': r['title'],
                'url': r['url'],
                'score': r['score'],
                'excerpt': r['chunk'][:200] + '...'
            }
            for r in results
        ]

        return {
            'question': question,
            'answer': answer,
            'sources': sources
        }

    def generate_ai_answer(self, question: str, context: str) -> str:
        """Generate AI answer using OpenAI"""
        try:
            prompt = f"""You are a federal regulatory compliance expert. Answer the question based ONLY on the context below.

REGULATORY CONTEXT:
{context}

QUESTION: {question}

ANSWER (cite specific sources):"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a regulatory compliance expert. Only use the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"AI generation failed: {e}"


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lightweight Federal Regulatory RAG System"
    )

    parser.add_argument(
        '--crawl',
        type=str,
        help='CSV file with URLs to crawl'
    )

    parser.add_argument(
        '--max-urls',
        type=int,
        default=10,
        help='Maximum URLs to crawl'
    )

    parser.add_argument(
        '--ask',
        type=str,
        help='Ask a question'
    )

    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI answer generation'
    )

    parser.add_argument(
        '--data-file',
        type=str,
        default='regulatory_content.json',
        help='Path to data file'
    )

    args = parser.parse_args()

    # Initialize RAG system
    rag = LightweightRAG(data_file=args.data_file)

    # Crawl if requested
    if args.crawl:
        rag.crawl_urls_from_csv(args.crawl, max_urls=args.max_urls)

    # Load existing data
    else:
        rag.load_documents()

    # Ask question if provided
    if args.ask:
        result = rag.ask(args.ask, use_ai=not args.no_ai)

        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(result['answer'])

        print("\n" + "=" * 80)
        print("SOURCES")
        print("=" * 80)
        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. {source['title']}")
            print(f"   URL: {source['url']}")
            print(f"   Score: {source['score']}")
        print("=" * 80)

    # Interactive mode
    elif not args.crawl:
        print("\nInteractive Mode (type 'exit' to quit)")
        print("=" * 80)

        while True:
            question = input("\nYour question: ").strip()

            if question.lower() in ['exit', 'quit', 'q']:
                break

            if not question:
                continue

            result = rag.ask(question, use_ai=not args.no_ai)

            print("\n" + "-" * 80)
            print(result['answer'])
            print("\n" + "-" * 80)
            print("SOURCES:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']} (Score: {source['score']})")


if __name__ == "__main__":
    main()
