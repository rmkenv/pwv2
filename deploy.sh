#!/bin/bash
# Complete Deployment Script for RAG System

echo "================================"
echo "RAG System Deployment"
echo "================================"

# Step 1: Install dependencies
echo ""
echo "Step 1: Installing dependencies..."
pip install -r requirements_complete.txt

# Step 2: Run crawler
echo ""
echo "Step 2: Crawling federal regulatory content..."
python federal_crawler.py --csv federal_dpw_compliance_resources.csv --max-urls 24

# Step 3: Process content
echo ""
echo "Step 3: Processing crawled content..."
python content_processor.py

# Step 4: Build vector database
echo ""
echo "Step 4: Building vector database..."
python build_vector_db.py --chunks-csv federal_crawl_output/processed_chunks.csv

# Step 5: Test query service
echo ""
echo "Step 5: Testing query service..."
python query_service.py --question "What are OSHA fall protection requirements?"

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "To start the API server:"
echo "  python api_server.py"
echo ""
echo "Or use uvicorn directly:"
echo "  uvicorn api_server:app --host 0.0.0.0 --port 8000"
