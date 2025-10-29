#!/usr/bin/env python3
"""
Query Service with AI Integration
Handles semantic search and AI-powered question answering
"""

import os
import json
from typing import List, Dict, Any, Optional
import numpy as np

# Import from build_vector_db
try:
    from build_vector_db import VectorDB, EmbeddingService
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

# For AI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class QueryService:
    """
    Query service for regulatory compliance questions
    Combines semantic search with AI-powered answers
    """

    def __init__(
        self,
        vector_db_path: str = "vector_db/regulatory_vector_db",
        model_name: str = "all-MiniLM-L6-v2",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize query service

        Args:
            vector_db_path: Path to vector database
            model_name: Embedding model name
            openai_api_key: OpenAI API key (optional)
        """
        # Load vector database
        print("Loading vector database...")
        self.vector_db = VectorDB()
        self.vector_db.load(vector_db_path)

        # Load embedding service
        print("Loading embedding model...")
        self.embedder = EmbeddingService(model_name=model_name)

        # Initialize OpenAI client if available
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if OPENAI_AVAILABLE and self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            print("✓ OpenAI client initialized")
        else:
            self.openai_client = None
            print("⚠ OpenAI not available - using keyword search only")

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search for relevant regulatory content

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional metadata filters

        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_texts([query])[0]

        # Search vector database
        results = self.vector_db.search(query_embedding, k=top_k * 2)

        # Apply filters if provided
        if filters:
            filtered_results = []
            for result in results:
                match = all(
                    result.get(key) == value
                    for key, value in filters.items()
                )
                if match:
                    filtered_results.append(result)
            results = filtered_results[:top_k]
        else:
            results = results[:top_k]

        return results

    def build_context(
        self,
        search_results: List[Dict[str, Any]],
        max_context_length: int = 6000
    ) -> str:
        """
        Build context string from search results

        Args:
            search_results: List of search result dicts
            max_context_length: Maximum context characters

        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0

        for i, result in enumerate(search_results, 1):
            chunk_text = result.get('chunk_text', '')
            source_title = result.get('source_title', 'Unknown')
            source_url = result.get('source_url', '')

            # Truncate if needed
            available_space = max_context_length - current_length
            if available_space < 200:
                break

            if len(chunk_text) > available_space:
                chunk_text = chunk_text[:available_space] + "..."

            part = f"""
[Source {i}] {source_title}
URL: {source_url}

{chunk_text}

---
"""

            context_parts.append(part)
            current_length += len(part)

        return "\n".join(context_parts)

    def generate_answer(
        self,
        question: str,
        context: str,
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Generate AI answer using OpenAI

        Args:
            question: User question
            context: Retrieved context
            model: OpenAI model name

        Returns:
            Generated answer
        """
        if not self.openai_client:
            return "OpenAI not available. Please configure API key."

        prompt = f"""You are a federal regulatory compliance expert. Answer the question based ONLY on the provided regulatory context below. Be precise and cite specific sources.

REGULATORY CONTEXT:
{context}

QUESTION: {question}

ANSWER (be specific and cite sources):"""

        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a precise regulatory compliance expert. Only use information from the provided context. Cite sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def ask(
        self,
        question: str,
        top_k: int = 5,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a compliance question

        Args:
            question: Compliance question
            top_k: Number of source documents to retrieve
            use_ai: Use AI to generate answer

        Returns:
            Dict with answer, sources, and metadata
        """
        print(f"\nProcessing question: {question}")

        # Semantic search
        search_results = self.semantic_search(question, top_k=top_k)

        if not search_results:
            return {
                'question': question,
                'answer': "No relevant regulatory content found for your question.",
                'sources': [],
                'context': ""
            }

        # Build context
        context = self.build_context(search_results)

        # Generate answer if AI available
        if use_ai and self.openai_client:
            answer = self.generate_answer(question, context)
        else:
            answer = "Relevant regulatory sources found. Review the sources below for detailed information."

        # Prepare sources
        sources = [
            {
                'title': r.get('source_title', 'Unknown'),
                'url': r.get('source_url', ''),
                'similarity_score': r.get('similarity_score', 0),
                'excerpt': r.get('chunk_text', '')[:200] + "..."
            }
            for r in search_results
        ]

        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'context': context,
            'num_sources': len(sources)
        }


def main():
    """Interactive query interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query federal regulatory compliance database"
    )

    parser.add_argument(
        '--vector-db',
        type=str,
        default='vector_db/regulatory_vector_db',
        help='Path to vector database'
    )

    parser.add_argument(
        '--question',
        type=str,
        help='Question to ask'
    )

    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI answer generation'
    )

    args = parser.parse_args()

    # Initialize service
    service = QueryService(vector_db_path=args.vector_db)

    if args.question:
        # Single question mode
        result = service.ask(args.question, use_ai=not args.no_ai)

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
            print(f"   Relevance: {source['similarity_score']:.2%}")
        print("=" * 80)

    else:
        # Interactive mode
        print("\nInteractive Query Mode (type 'exit' to quit)")
        print("=" * 80)

        while True:
            question = input("\nYour question: ").strip()

            if question.lower() in ['exit', 'quit', 'q']:
                break

            if not question:
                continue

            result = service.ask(question, use_ai=not args.no_ai)

            print("\n" + "-" * 80)
            print("ANSWER:")
            print("-" * 80)
            print(result['answer'])
            print("\n" + "-" * 80)
            print("SOURCES:")
            print("-" * 80)
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']} (Relevance: {source['similarity_score']:.0%})")
                print(f"   {source['url']}")
            print("-" * 80)


if __name__ == "__main__":
    main()
