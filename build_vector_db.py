#!/usr/bin/env python3
"""
Complete Embedding and Vector Database System
Generates embeddings and builds searchable FAISS index
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

# For production use
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠ sentence-transformers not installed. Install with:")
    print("  pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠ faiss not installed. Install with:")
    print("  pip install faiss-cpu")


class EmbeddingService:
    """Generate embeddings using Sentence Transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service

        Args:
            model_name: Sentence Transformers model name
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required")

        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        print(f"✓ Model loaded (dimension: {self.embedding_dim})")

    def embed_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for texts

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            NumPy array of embeddings
        """
        print(f"Generating embeddings for {len(texts)} texts...")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        print(f"✓ Generated {len(embeddings)} embeddings")

        return embeddings

    def embed_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = 'chunk_text'
    ) -> pd.DataFrame:
        """
        Add embeddings to DataFrame

        Args:
            df: DataFrame with text
            text_column: Column containing text

        Returns:
            DataFrame with embeddings column
        """
        texts = df[text_column].tolist()
        embeddings = self.embed_texts(texts)

        df['embedding'] = [emb.tolist() for emb in embeddings]

        return df


class VectorDB:
    """FAISS-based vector database for semantic search"""

    def __init__(self, dimension: int = 384):
        """
        Initialize vector database

        Args:
            dimension: Embedding dimension
        """
        if not FAISS_AVAILABLE:
            raise ImportError("faiss-cpu or faiss-gpu is required")

        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        self.is_built = False

    def add_vectors(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]]
    ):
        """
        Add vectors and metadata to database

        Args:
            embeddings: NumPy array of embeddings
            metadata: List of metadata dicts
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embeddings dimension {embeddings.shape[1]} != {self.dimension}")

        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')

        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(metadata)
        self.is_built = True

        print(f"✓ Added {len(embeddings)} vectors to database")
        print(f"  Total vectors: {self.index.ntotal}")

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for most similar vectors

        Args:
            query_vector: Query embedding
            k: Number of results

        Returns:
            List of results with metadata and scores
        """
        if not self.is_built:
            return []

        # Ensure query is 2D array
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        query_vector = query_vector.astype('float32')

        # Search
        distances, indices = self.index.search(query_vector, k)

        # Build results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['distance'] = float(dist)
                result['similarity_score'] = 1 / (1 + float(dist))  # Convert distance to similarity
                result['rank'] = i + 1
                results.append(result)

        return results

    def save(self, filepath: str):
        """Save vector database to disk"""
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.faiss")

        # Save metadata
        with open(f"{filepath}.metadata.pkl", 'wb') as f:
            pickle.dump(self.metadata, f)

        print(f"✓ Saved vector database to {filepath}")

    def load(self, filepath: str):
        """Load vector database from disk"""
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.faiss")

        # Load metadata
        with open(f"{filepath}.metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)

        self.is_built = True

        print(f"✓ Loaded vector database from {filepath}")
        print(f"  Total vectors: {self.index.ntotal}")


def build_complete_vector_database(
    chunks_csv_path: str,
    output_dir: str = "vector_db",
    model_name: str = "all-MiniLM-L6-v2"
):
    """
    Build complete vector database from processed chunks

    Args:
        chunks_csv_path: Path to processed chunks CSV
        output_dir: Output directory for vector DB
        model_name: Sentence Transformers model name
    """
    print("=" * 80)
    print("BUILDING VECTOR DATABASE")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load processed chunks
    print(f"Loading chunks from: {chunks_csv_path}")
    df = pd.read_csv(chunks_csv_path)
    print(f"✓ Loaded {len(df)} chunks\n")

    # Initialize embedding service
    embedder = EmbeddingService(model_name=model_name)

    # Generate embeddings
    texts = df['chunk_text'].tolist()
    embeddings = embedder.embed_texts(texts)

    # Create vector database
    print(f"\nCreating vector database...")
    vector_db = VectorDB(dimension=embedder.embedding_dim)

    # Prepare metadata
    metadata = df.to_dict('records')

    # Add to database
    vector_db.add_vectors(embeddings, metadata)

    # Save database
    db_path = os.path.join(output_dir, "regulatory_vector_db")
    vector_db.save(db_path)

    # Save embedding model info
    info = {
        'model_name': model_name,
        'embedding_dim': embedder.embedding_dim,
        'total_chunks': len(df),
        'created_date': pd.Timestamp.now().isoformat()
    }

    with open(os.path.join(output_dir, "db_info.json"), 'w') as f:
        import json
        json.dump(info, f, indent=2)

    print("\n" + "=" * 80)
    print("VECTOR DATABASE BUILD COMPLETE")
    print("=" * 80)
    print(f"Location: {output_dir}/")
    print(f"Total vectors: {vector_db.index.ntotal}")
    print(f"Dimension: {embedder.embedding_dim}")
    print("=" * 80)

    return vector_db, embedder


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build vector database from processed chunks"
    )

    parser.add_argument(
        '--chunks-csv',
        type=str,
        default='federal_crawl_output/processed_chunks.csv',
        help='Path to processed chunks CSV'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='vector_db',
        help='Output directory for vector database'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence Transformers model name'
    )

    args = parser.parse_args()

    build_complete_vector_database(
        chunks_csv_path=args.chunks_csv,
        output_dir=args.output_dir,
        model_name=args.model
    )


if __name__ == "__main__":
    main()
