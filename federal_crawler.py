#!/usr/bin/env python3
"""
Federal Regulatory Content Crawler
Focused crawler for federal government URLs with recursive child page discovery
"""

import os
import re
import json
import time
import hashlib
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup
import pandas as pd

# For PDF support
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("⚠ PyMuPDF not installed. PDF extraction disabled.")
    print("  Install with: pip install PyMuPDF")


class FederalURLCrawler:
    """
    Crawler specifically designed for federal government regulatory URLs
    Handles recursive crawling of child pages within same domain
    """

    def __init__(
        self,
        output_dir: str = "federal_crawl_output",
        max_depth: int = 2,
        delay_seconds: float = 2.0,
        max_pages_per_domain: int = 100
    ):
        """
        Initialize the federal URL crawler

        Args:
            output_dir: Directory to save crawled content
            max_depth: Maximum crawl depth (0=main page only, 1=+children, 2=+grandchildren)
            delay_seconds: Delay between requests (be polite!)
            max_pages_per_domain: Maximum pages to crawl per domain
        """
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.delay_seconds = delay_seconds
        self.max_pages_per_domain = max_pages_per_domain

        # Create output directories
        os.makedirs(f"{output_dir}/content", exist_ok=True)
        os.makedirs(f"{output_dir}/logs", exist_ok=True)

        # Tracking
        self.visited_urls = set()
        self.domain_page_counts = {}
        self.crawled_pages = []
        self.failed_urls = []

        # User agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; DPW-Compliance-Research/1.0; Educational)'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def is_federal_domain(self, url: str) -> bool:
        """Check if URL is a federal government domain"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        federal_patterns = [
            '.gov',           # All .gov domains
            'govinfo.gov',
            'gpo.gov',
            'osha.gov',
            'epa.gov',
            'dot.gov',
            'fhwa.dot.gov',
            'nhtsa.gov',
            'congress.gov',
            'archives.gov',
            'regulations.gov'
        ]

        return any(pattern in domain for pattern in federal_patterns)

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL should be crawled"""
        try:
            parsed = urlparse(url)

            # Must be http/https
            if parsed.scheme not in ['http', 'https']:
                return False

            # Must be federal domain
            if not self.is_federal_domain(url):
                return False

            # Stay within same domain (or allow subdomains)
            url_domain = parsed.netloc.lower()
            if base_domain not in url_domain and url_domain not in base_domain:
                return False

            # Skip common non-content URLs
            skip_patterns = [
                r'/search\?',
                r'/login',
                r'/signin',
                r'/register',
                r'/print\?',
                r'\.jpg$', r'\.png$', r'\.gif$', r'\.svg$',
                r'\.css$', r'\.js$', r'\.ico$',
                r'\.zip$', r'\.tar$', r'\.gz$',
                r'/rss', r'/feed',
                r'/share\?', r'/email\?'
            ]

            url_lower = url.lower()
            for pattern in skip_patterns:
                if re.search(pattern, url_lower):
                    return False

            return True

        except Exception:
            return False

    def extract_text_from_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract clean text and links from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script, style, nav, footer, header elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Get title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Untitled"

        # Try to find main content
        main_content = None
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            '.page-content',
            '.body-content'
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # Fallback to body
        if not main_content:
            main_content = soup.find('body')

        # Extract text
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)

        # Extract internal links
        links = []
        base_domain = urlparse(url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)

            if self.is_valid_url(absolute_url, base_domain):
                links.append(absolute_url)

        # Remove duplicate links
        links = list(set(links))

        return {
            'title': title_text,
            'text': clean_text,
            'links': links,
            'text_length': len(clean_text)
        }

    def extract_text_from_pdf(self, pdf_url: str) -> Dict[str, Any]:
        """Download and extract text from PDF"""
        if not PDF_SUPPORT:
            return {'title': 'PDF (extraction not available)', 'text': '', 'links': []}

        try:
            # Download PDF
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()

            # Open PDF from memory
            doc = fitz.open(stream=response.content, filetype="pdf")

            # Extract text from all pages
            text_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_parts.append(page.get_text())

            full_text = '\n'.join(text_parts)

            # Get title from metadata or first line
            title = doc.metadata.get('title', '')
            if not title:
                first_lines = full_text.split('\n')[:3]
                title = ' '.join(first_lines)[:100]

            doc.close()

            return {
                'title': title or f"PDF from {urlparse(pdf_url).path}",
                'text': full_text,
                'links': [],
                'text_length': len(full_text)
            }

        except Exception as e:
            print(f"    ⚠ PDF extraction error: {e}")
            return {'title': 'PDF (extraction failed)', 'text': '', 'links': []}

    def crawl_url(
        self,
        url: str,
        depth: int = 0,
        parent_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crawl a single URL and return extracted content

        Args:
            url: URL to crawl
            depth: Current crawl depth
            parent_url: URL of parent page

        Returns:
            Dict with extracted content or None if failed
        """

        # Check if already visited
        if url in self.visited_urls:
            return None

        # Check depth limit
        if depth > self.max_depth:
            return None

        # Check domain page limit
        domain = urlparse(url).netloc
        if self.domain_page_counts.get(domain, 0) >= self.max_pages_per_domain:
            print(f"  ⚠ Reached page limit for {domain}")
            return None

        self.visited_urls.add(url)
        self.domain_page_counts[domain] = self.domain_page_counts.get(domain, 0) + 1

        # Display progress
        indent = "  " * depth
        print(f"{indent}→ [{depth}] {url}")

        try:
            # Respect rate limiting
            time.sleep(self.delay_seconds)

            # Make request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Determine content type
            content_type = response.headers.get('Content-Type', '').lower()

            # Extract content based on type
            if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                extracted = self.extract_text_from_pdf(url)
                source_type = 'pdf'
            else:
                extracted = self.extract_text_from_html(response.text, url)
                source_type = 'html'

            # Create content object
            content = {
                'url': url,
                'title': extracted['title'],
                'content_text': extracted['text'],
                'content_length': extracted['text_length'],
                'source_type': source_type,
                'depth': depth,
                'parent_url': parent_url,
                'child_links': extracted['links'],
                'crawl_timestamp': datetime.now().isoformat(),
                'status_code': response.status_code
            }

            self.crawled_pages.append(content)

            print(f"{indent}  ✓ Extracted {extracted['text_length']} chars, found {len(extracted['links'])} links")

            # Save individual page content
            self.save_page_content(content)

            return content

        except Exception as e:
            print(f"{indent}  ✗ Error: {e}")
            self.failed_urls.append({'url': url, 'error': str(e), 'depth': depth})
            return None

    def save_page_content(self, content: Dict[str, Any]):
        """Save individual page content to JSON file"""
        # Create safe filename from URL
        url_hash = hashlib.md5(content['url'].encode()).hexdigest()[:12]
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', content['title'])[:50]
        filename = f"{url_hash}_{safe_title}.json"

        filepath = os.path.join(self.output_dir, 'content', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def crawl_with_children(
        self,
        start_url: str,
        max_pages: Optional[int] = None
    ):
        """
        Crawl URL and all its children using breadth-first search

        Args:
            start_url: Starting URL
            max_pages: Maximum total pages to crawl from this URL
        """

        print(f"\nStarting crawl from: {start_url}")
        print(f"Max depth: {self.max_depth}")
        print("-" * 80)

        # Queue: (url, depth, parent_url)
        queue = deque([(start_url, 0, None)])
        pages_crawled = 0

        while queue and (max_pages is None or pages_crawled < max_pages):
            url, depth, parent = queue.popleft()

            # Skip if already visited
            if url in self.visited_urls:
                continue

            # Crawl this URL
            content = self.crawl_url(url, depth, parent)

            if content:
                pages_crawled += 1

                # Add child links to queue if within depth limit
                if depth < self.max_depth:
                    for child_url in content['child_links']:
                        if child_url not in self.visited_urls:
                            queue.append((child_url, depth + 1, url))

        print(f"\n✓ Crawled {pages_crawled} pages from {start_url}")

    def crawl_from_csv(
        self,
        csv_path: str,
        jurisdiction_filter: str = "Federal",
        max_urls: Optional[int] = None
    ):
        """
        Crawl all federal URLs from compliance CSV

        Args:
            csv_path: Path to regulations CSV
            jurisdiction_filter: Filter for jurisdiction (default: "Federal")
            max_urls: Maximum URLs to process
        """

        print("=" * 80)
        print("FEDERAL REGULATORY CONTENT CRAWLER")
        print("=" * 80)
        print()

        # Load CSV
        print(f"Loading URLs from: {csv_path}")
        df = pd.read_csv(csv_path)

        # Filter for federal jurisdiction
        if jurisdiction_filter:
            df = df[df['Jurisdiction'] == jurisdiction_filter]

        # Get unique URLs
        urls = df['URL'].dropna().unique().tolist()

        if max_urls:
            urls = urls[:max_urls]

        print(f"Found {len(urls)} federal URLs to crawl")
        print(f"Crawl depth: {self.max_depth} (0=main page, 1=+children, 2=+grandchildren)")
        print()

        # Crawl each URL with its children
        for i, url in enumerate(urls, 1):
            print(f"\n{'=' * 80}")
            print(f"[{i}/{len(urls)}] Processing: {url}")
            print('=' * 80)

            try:
                self.crawl_with_children(url)
            except Exception as e:
                print(f"⚠ Failed to crawl {url}: {e}")
                self.failed_urls.append({'url': url, 'error': str(e), 'depth': 0})

        # Save summary
        self.save_crawl_summary()

    def save_crawl_summary(self):
        """Save summary of crawl results"""

        print("\n" + "=" * 80)
        print("CRAWL SUMMARY")
        print("=" * 80)

        print(f"\nTotal pages crawled: {len(self.crawled_pages)}")
        print(f"Failed URLs: {len(self.failed_urls)}")
        print(f"Unique domains: {len(self.domain_page_counts)}")

        # Domain breakdown
        print("\nPages per domain:")
        for domain, count in sorted(self.domain_page_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {domain}: {count} pages")

        # Save master index
        index_file = f"{self.output_dir}/crawl_index.json"
        index = {
            'crawl_date': datetime.now().isoformat(),
            'total_pages': len(self.crawled_pages),
            'failed_urls': len(self.failed_urls),
            'max_depth': self.max_depth,
            'pages': self.crawled_pages,
            'failed': self.failed_urls,
            'domain_counts': self.domain_page_counts
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved crawl index: {index_file}")

        # Save CSV summary
        csv_file = f"{self.output_dir}/crawled_federal_content.csv"
        df = pd.DataFrame(self.crawled_pages)

        # Select key columns
        columns = ['url', 'title', 'content_length', 'source_type', 'depth', 'parent_url', 'crawl_timestamp']
        df_summary = df[columns]
        df_summary.to_csv(csv_file, index=False)

        print(f"✓ Saved CSV summary: {csv_file}")

        # Save full content CSV
        full_csv = f"{self.output_dir}/crawled_federal_full_text.csv"
        df.to_csv(full_csv, index=False)

        print(f"✓ Saved full text CSV: {full_csv}")

        # Save failed URLs log
        if self.failed_urls:
            failed_file = f"{self.output_dir}/logs/failed_urls.json"
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_urls, f, indent=2)
            print(f"✓ Saved failed URLs log: {failed_file}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Federal Regulatory Content Crawler"
    )

    parser.add_argument(
        '--csv',
        type=str,
        default='ai_enhanced_dpw_compliance_resources.csv',
        help='Path to regulations CSV'
    )

    parser.add_argument(
        '--max-urls',
        type=int,
        help='Maximum URLs to crawl from CSV'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=2,
        help='Maximum crawl depth (0=main, 1=+children, 2=+grandchildren)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds'
    )

    parser.add_argument(
        '--max-pages-per-domain',
        type=int,
        default=100,
        help='Maximum pages to crawl per domain'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='federal_crawl_output',
        help='Output directory'
    )

    args = parser.parse_args()

    # Initialize crawler
    crawler = FederalURLCrawler(
        output_dir=args.output_dir,
        max_depth=args.max_depth,
        delay_seconds=args.delay,
        max_pages_per_domain=args.max_pages_per_domain
    )

    # Start crawling
    crawler.crawl_from_csv(
        csv_path=args.csv,
        jurisdiction_filter="Federal",
        max_urls=args.max_urls
    )


if __name__ == "__main__":
    main()
