
# Create a simple wrapper AI system that uses the crawled content

wrapper_ai = '''#!/usr/bin/env python3
"""
AI Wrapper for Federal Regulatory Compliance
Uses crawled content + LLM to answer compliance questions
"""

import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd

# For production: pip install openai anthropic
# Uncomment when ready:
# from openai import OpenAI
# from anthropic import Anthropic


class RegulatoryAIWrapper:
    """
    Simple AI wrapper that uses crawled regulatory content
    to answer compliance questions
    """
    
    def __init__(
        self,
        crawled_data_dir: str = "federal_crawl_output",
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        use_anthropic: bool = False
    ):
        """
        Initialize AI wrapper
        
        Args:
            crawled_data_dir: Directory with crawled content
            api_key: OpenAI or Anthropic API key
            model: Model to use
            use_anthropic: Use Anthropic Claude instead of OpenAI
        """
        self.crawled_data_dir = crawled_data_dir
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.use_anthropic = use_anthropic
        
        # Initialize AI client (uncomment in production)
        # if use_anthropic:
        #     self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        # else:
        #     self.client = OpenAI(api_key=self.api_key)
        
        # Load crawled content index
        self.content_index = self.load_content_index()
    
    def load_content_index(self) -> List[Dict[str, Any]]:
        """Load crawled content from index"""
        index_file = f"{self.crawled_data_dir}/crawl_index.json"
        
        if not os.path.exists(index_file):
            print(f"⚠ No crawl index found at {index_file}")
            print("Run federal_crawler.py first to crawl content")
            return []
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        pages = index.get('pages', [])
        print(f"Loaded {len(pages)} crawled pages")
        
        return pages
    
    def search_relevant_content(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword search for relevant content
        (In production, use vector embeddings for better results)
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of relevant content dicts
        """
        
        # Simple keyword matching (improve with embeddings in production)
        query_terms = query.lower().split()
        
        scored_pages = []
        for page in self.content_index:
            text = page.get('content_text', '').lower()
            title = page.get('title', '').lower()
            
            # Score based on keyword matches
            score = 0
            for term in query_terms:
                score += text.count(term) * 1
                score += title.count(term) * 5  # Title matches weighted higher
            
            if score > 0:
                scored_pages.append((score, page))
        
        # Sort by score and return top results
        scored_pages.sort(reverse=True, key=lambda x: x[0])
        top_pages = [page for score, page in scored_pages[:max_results]]
        
        print(f"Found {len(top_pages)} relevant pages for query: '{query}'")
        
        return top_pages
    
    def build_context(
        self,
        relevant_pages: List[Dict[str, Any]],
        max_context_length: int = 8000
    ) -> str:
        """
        Build context string from relevant pages
        
        Args:
            relevant_pages: List of page dicts
            max_context_length: Maximum characters for context
            
        Returns:
            Formatted context string
        """
        
        context_parts = []
        current_length = 0
        
        for page in relevant_pages:
            url = page['url']
            title = page['title']
            content = page['content_text']
            
            # Truncate content if needed
            available_space = max_context_length - current_length
            if available_space < 500:  # Need at least 500 chars
                break
            
            if len(content) > available_space:
                content = content[:available_space] + "... [truncated]"
            
            part = f"""
SOURCE: {title}
URL: {url}

{content}

---
"""
            
            context_parts.append(part)
            current_length += len(part)
        
        return "\\n".join(context_parts)
    
    def ask_compliance_question(
        self,
        question: str,
        document_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask a compliance question using AI + crawled regulatory content
        
        Args:
            question: Compliance question
            document_text: Optional document text to check (e.g., SOP)
            
        Returns:
            Dict with answer and sources
        """
        
        print(f"\\nProcessing question: {question}")
        print("-" * 80)
        
        # Search for relevant regulatory content
        relevant_pages = self.search_relevant_content(question, max_results=5)
        
        if not relevant_pages:
            return {
                'answer': "No relevant regulatory content found. Try rephrasing your question.",
                'sources': []
            }
        
        # Build context from relevant pages
        context = self.build_context(relevant_pages, max_context_length=8000)
        
        # Build prompt
        prompt = self.build_prompt(question, context, document_text)
        
        # Call AI model (mock response for demo)
        print("Generating AI response...")
        
        # In production, uncomment:
        # response = self.call_ai_model(prompt)
        
        # Mock response for demo
        response = f"""Based on the federal regulations provided:

**Answer:**
{question}

The relevant regulations indicate specific requirements that must be met. Please review the following sources for complete details.

**Key Requirements:**
1. Compliance with federal safety standards
2. Proper documentation and record-keeping
3. Regular inspections and updates

**Recommendations:**
- Review the cited regulations in detail
- Ensure all requirements are documented in your SOP
- Schedule regular compliance audits

Please note: This is a preliminary analysis. Consult the full regulatory text and legal counsel for authoritative guidance.
"""
        
        # Extract sources
        sources = [
            {'title': page['title'], 'url': page['url']}
            for page in relevant_pages
        ]
        
        return {
            'answer': response,
            'sources': sources,
            'context_used': context[:500] + "..." if len(context) > 500 else context
        }
    
    def build_prompt(
        self,
        question: str,
        context: str,
        document_text: Optional[str] = None
    ) -> str:
        """Build prompt for AI model"""
        
        if document_text:
            prompt = f"""You are a compliance expert analyzing documents against federal regulations.

REGULATORY CONTEXT (from official federal sources):
{context}

DOCUMENT TO ANALYZE:
{document_text[:2000]}...

QUESTION:
{question}

Provide a detailed compliance analysis including:
1. Direct answer to the question
2. Specific regulatory requirements that apply
3. Any gaps or missing requirements
4. Recommendations for compliance

Base your answer ONLY on the regulatory context provided above.
"""
        else:
            prompt = f"""You are a compliance expert answering questions about federal regulations.

REGULATORY CONTEXT (from official federal sources):
{context}

QUESTION:
{question}

Provide a clear, detailed answer based on the regulatory context above. Include:
1. Direct answer to the question
2. Specific regulatory citations
3. Key requirements
4. Any important caveats or conditions

Base your answer ONLY on the regulatory context provided above.
"""
        
        return prompt
    
    def call_ai_model(self, prompt: str) -> str:
        """
        Call AI model with prompt
        (Implement with actual API calls in production)
        """
        
        # OpenAI example (uncomment in production):
        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {"role": "system", "content": "You are a federal regulatory compliance expert."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.3
        # )
        # return response.choices[0].message.content
        
        # Anthropic example (uncomment in production):
        # if self.use_anthropic:
        #     message = self.client.messages.create(
        #         model="claude-3-sonnet-20240229",
        #         max_tokens=2000,
        #         messages=[{"role": "user", "content": prompt}]
        #     )
        #     return message.content[0].text
        
        return "Mock AI response (implement with real API)"
    
    def check_sop_compliance(
        self,
        sop_file: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check SOP compliance against crawled federal regulations
        
        Args:
            sop_file: Path to SOP file
            output_file: Optional path to save report
            
        Returns:
            Compliance report dict
        """
        
        print(f"\\nChecking SOP compliance: {sop_file}")
        print("=" * 80)
        
        # Read SOP
        with open(sop_file, 'r') as f:
            sop_text = f.read()
        
        print(f"SOP length: {len(sop_text)} characters\\n")
        
        # Generate compliance questions based on SOP sections
        questions = [
            "What are the OSHA safety requirements for construction sites?",
            "What environmental protection requirements must be followed?",
            "What are the documentation and record-keeping requirements?",
            "What training requirements apply to workers?",
            "What are the emergency response requirements?"
        ]
        
        results = []
        for question in questions:
            result = self.ask_compliance_question(question, sop_text)
            results.append({
                'question': question,
                'answer': result['answer'],
                'sources': result['sources']
            })
        
        # Build report
        report = self.build_compliance_report(sop_file, results)
        
        # Save report
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\\n✓ Saved compliance report: {output_file}")
        
        return {
            'sop_file': sop_file,
            'results': results,
            'report': report
        }
    
    def build_compliance_report(
        self,
        sop_file: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """Build markdown compliance report"""
        
        report_lines = []
        report_lines.append(f"# Compliance Analysis Report")
        report_lines.append(f"\\n**Document:** {sop_file}")
        report_lines.append(f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append(f"**Regulatory Sources:** {len(self.content_index)} federal pages")
        report_lines.append("\\n---\\n")
        
        for i, result in enumerate(results, 1):
            report_lines.append(f"\\n## Question {i}: {result['question']}\\n")
            report_lines.append(result['answer'])
            report_lines.append("\\n### Sources:\\n")
            
            for source in result['sources']:
                report_lines.append(f"- [{source['title']}]({source['url']})")
            
            report_lines.append("\\n---\\n")
        
        return "\\n".join(report_lines)


def main():
    """Example usage"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Wrapper for Federal Regulatory Compliance"
    )
    
    parser.add_argument(
        '--ask',
        type=str,
        help='Ask a compliance question'
    )
    
    parser.add_argument(
        '--check-sop',
        type=str,
        help='Check SOP file for compliance'
    )
    
    parser.add_argument(
        '--crawled-data',
        type=str,
        default='federal_crawl_output',
        help='Directory with crawled content'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for report'
    )
    
    args = parser.parse_args()
    
    # Initialize wrapper
    wrapper = RegulatoryAIWrapper(
        crawled_data_dir=args.crawled_data
    )
    
    if args.ask:
        # Answer single question
        result = wrapper.ask_compliance_question(args.ask)
        print("\\n" + "=" * 80)
        print("ANSWER:")
        print("=" * 80)
        print(result['answer'])
        print("\\n" + "=" * 80)
        print("SOURCES:")
        print("=" * 80)
        for source in result['sources']:
            print(f"- {source['title']}")
            print(f"  {source['url']}")
    
    elif args.check_sop:
        # Check SOP compliance
        result = wrapper.check_sop_compliance(
            args.check_sop,
            output_file=args.output or 'compliance_report.md'
        )
        print("\\n✓ Compliance check complete")
    
    else:
        print("Usage:")
        print("  python ai_wrapper.py --ask 'What are OSHA fall protection requirements?'")
        print("  python ai_wrapper.py --check-sop my_sop.txt --output report.md")


if __name__ == "__main__":
    main()
'''

with open('ai_wrapper.py', 'w') as f:
    f.write(wrapper_ai)

print("✓ Created: ai_wrapper.py")
print("  AI wrapper that uses crawled content to answer questions")
print()
