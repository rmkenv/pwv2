#!/usr/bin/env python3
"""
Content Processor for RAG System
Loads crawled data, cleans text, and chunks for embedding
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


class ContentProcessor:
    """Process crawled regulatory content for embedding"""

    def __init__(self, crawled_data_dir: str = "federal_crawl_output"):
        self.crawled_data_dir = crawled_data_dir

    def load_crawled_content(self) -> pd.DataFrame:
        """Load crawled content from CSV"""
        csv_path = f"{self.crawled_data_dir}/crawled_federal_full_text.csv"

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Crawled content not found at {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} crawled documents")

        return df

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')

        return text.strip()

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period + space in last 100 chars
                search_start = max(start, end - 100)
                last_period = text.rfind('. ', search_start, end)

                if last_period != -1 and last_period > start:
                    end = last_period + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < len(text) else len(text)

        return chunks

    def process_documents(
        self,
        df: pd.DataFrame,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> pd.DataFrame:
        """
        Process all documents into chunks

        Args:
            df: DataFrame with crawled content
            chunk_size: Chunk size
            overlap: Chunk overlap

        Returns:
            DataFrame with chunks and metadata
        """
        print(f"\nProcessing {len(df)} documents into chunks...")

        all_chunks = []

        for idx, row in df.iterrows():
            # Clean text
            text = self.clean_text(row.get('content_text', ''))

            if not text or len(text) < 50:  # Skip very short content
                continue

            # Chunk text
            chunks = self.chunk_text(text, chunk_size, overlap)

            # Create chunk records
            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'source_url': row.get('url', ''),
                    'source_title': row.get('title', 'Untitled'),
                    'source_type': row.get('source_type', 'unknown'),
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'chunk_text': chunk,
                    'chunk_length': len(chunk),
                    'crawl_date': row.get('crawl_timestamp', ''),
                    'depth': row.get('depth', 0)
                })

            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(df)} documents...")

        chunks_df = pd.DataFrame(all_chunks)
        print(f"\n✓ Created {len(chunks_df)} chunks from {len(df)} documents")

        return chunks_df

    def save_processed_chunks(
        self,
        chunks_df: pd.DataFrame,
        output_file: str = "processed_chunks.csv"
    ) -> str:
        """Save processed chunks to CSV"""
        output_path = f"{self.crawled_data_dir}/{output_file}"
        chunks_df.to_csv(output_path, index=False)

        print(f"✓ Saved processed chunks to: {output_path}")

        return output_path

    def get_statistics(self, chunks_df: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        stats = {
            'total_chunks': len(chunks_df),
            'unique_sources': chunks_df['source_url'].nunique(),
            'avg_chunk_length': chunks_df['chunk_length'].mean(),
            'total_characters': chunks_df['chunk_length'].sum(),
            'source_types': chunks_df['source_type'].value_counts().to_dict()
        }

        return stats


def main():
    """Main processing pipeline"""

    processor = ContentProcessor()

    # Load crawled content
    df = processor.load_crawled_content()

    # Process into chunks
    chunks_df = processor.process_documents(df, chunk_size=1000, overlap=200)

    # Save processed chunks
    processor.save_processed_chunks(chunks_df)

    # Print statistics
    stats = processor.get_statistics(chunks_df)

    print("\n" + "=" * 80)
    print("PROCESSING STATISTICS")
    print("=" * 80)
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Unique sources: {stats['unique_sources']}")
    print(f"Average chunk length: {stats['avg_chunk_length']:.0f} characters")
    print(f"Total content: {stats['total_characters']:,} characters")
    print(f"\nSource types: {stats['source_types']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
