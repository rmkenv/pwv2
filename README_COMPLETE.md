# Federal Regulatory Compliance RAG System
## Complete Production-Ready Implementation

A retrieval-augmented generation (RAG) system that provides precise, up-to-date, and verifiable answers to federal regulatory compliance questions.

---

## 🎯 What This System Does

- **Crawls** official federal regulatory websites (OSHA, EPA, GovInfo, etc.)
- **Extracts** full text from HTML and PDF documents
- **Processes** content into searchable chunks
- **Generates** semantic embeddings for all regulatory content
- **Searches** using vector similarity for relevant regulations
- **Answers** questions with AI, citing specific sources
- **Provides** verifiable citations back to original documents

---

## 📦 Complete System Components

### 1. Data Collection Layer
- `federal_crawler.py` - Automated web crawler
- Handles HTML and PDF extraction
- Recursive child page discovery
- Configurable depth and rate limiting

### 2. Processing Layer
- `content_processor.py` - Text cleaning and chunking
- Normalizes regulatory text
- Creates overlapping 1000-char chunks
- Preserves source metadata

### 3. Embedding & Search Layer
- `build_vector_db.py` - Vector database builder
- Uses Sentence Transformers for embeddings
- FAISS for fast similarity search
- Supports millions of documents

### 4. AI Query Layer
- `query_service.py` - Semantic search + AI answering
- Retrieves relevant regulatory chunks
- Integrates with OpenAI GPT-4
- Returns answers with citations

### 5. API Layer
- `api_server.py` - FastAPI REST server
- `/query` endpoint for Q&A
- `/search` endpoint for document retrieval
- `/health` for system status

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- 8GB+ RAM
- 50GB+ disk space

### Installation

```bash
# Clone or download all files to a directory
cd compliance-rag-system

# Install dependencies
pip install -r requirements_complete.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Run Complete Pipeline

```bash
# Option 1: Automated deployment script
chmod +x deploy.sh
./deploy.sh

# Option 2: Manual step-by-step
# Step 1: Crawl content
python federal_crawler.py --csv federal_dpw_compliance_resources.csv --max-urls 5

# Step 2: Process content
python content_processor.py

# Step 3: Build vector database
python build_vector_db.py

# Step 4: Test query service
python query_service.py --question "What are OSHA requirements for fall protection?"

# Step 5: Start API server
python api_server.py
```

---

## 💻 Usage Examples

### Command Line

```bash
# Ask a question
python query_service.py --question "What are EPA stormwater regulations?"

# Interactive mode
python query_service.py
```

### API Usage

```bash
# Start server
python api_server.py

# Query endpoint
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are OSHA requirements?", "top_k": 5}'

# Search endpoint
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"question": "fall protection", "top_k": 10}'

# Health check
curl "http://localhost:8000/health"
```

### Python Integration

```python
from query_service import QueryService

# Initialize
service = QueryService(vector_db_path="vector_db/regulatory_vector_db")

# Ask question
result = service.ask("What are OSHA requirements for scaffolding?")

print(result['answer'])
for source in result['sources']:
    print(f"- {source['title']}: {source['url']}")
```

---

## 🐳 Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build manually
docker build -t compliance-rag .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key compliance-rag
```

---

## ☁️ Cloud Deployment

### AWS EC2

```bash
# Launch t3.large instance (recommended)
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Clone repo
git clone your-repo-url
cd compliance-rag-system

# Run deployment
./deploy.sh

# Start API server as service
nohup python api_server.py > api.log 2>&1 &
```

### Google Cloud

```bash
# Create VM instance
gcloud compute instances create compliance-rag \
  --machine-type=n1-standard-4 \
  --zone=us-central1-a

# SSH and deploy
gcloud compute ssh compliance-rag
# ... same as AWS
```

---

## 📊 System Architecture

```
User Question
     ↓
[Query Service]
     ↓
[Embed Question] ← Sentence Transformers
     ↓
[Vector Search] ← FAISS Index
     ↓
[Top K Results] (relevant regulatory chunks)
     ↓
[Build Context] (concatenate chunks)
     ↓
[AI Generation] ← OpenAI GPT-4
     ↓
[Answer + Citations]
```

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
crawler:
  max_depth: 2              # Crawl depth
  delay_seconds: 2.0        # Politeness delay

processor:
  chunk_size: 1000          # Characters per chunk
  chunk_overlap: 200        # Overlap for context

embeddings:
  model_name: "all-MiniLM-L6-v2"  # Embedding model

ai:
  model: "gpt-4o-mini"      # OpenAI model
  temperature: 0.3          # Response randomness
```

---

## 📈 Performance & Scaling

### Expected Performance

| Metric | Value |
|--------|-------|
| Crawl 24 URLs @ depth 2 | 15-30 minutes |
| Process content | 5-10 minutes |
| Generate embeddings | 10-30 minutes (CPU) |
| Build vector DB | 5 minutes |
| Query latency | 2-5 seconds |
| Concurrent users | 10-50 (single instance) |

### Scaling Options

- **Horizontal**: Deploy multiple API instances behind load balancer
- **Vertical**: Increase CPU/RAM for faster embedding/search
- **GPU**: Use faiss-gpu for 10-100x faster search
- **Caching**: Add Redis for frequently asked questions

---

## 💰 Cost Estimates

### Free Tier (Local)
- Crawling: $0
- Embeddings: $0 (local models)
- Vector DB: $0 (FAISS)
- **Total: $0/month**

### Production (Cloud + OpenAI)
- EC2 t3.large: $60/month
- Storage: $10/month
- OpenAI API: $20-50/month (1000-2500 queries)
- **Total: $90-120/month**

---

## 🔧 Maintenance

### Regular Updates

```bash
# Weekly: Update regulatory content
python federal_crawler.py --csv federal_dpw_compliance_resources.csv
python content_processor.py
python build_vector_db.py

# Monthly: Full rebuild
rm -rf federal_crawl_output vector_db
./deploy.sh
```

### Monitoring

- Check `/health` endpoint regularly
- Monitor API logs for errors
- Track query latency and accuracy
- Review failed crawl URLs

---

## 🐛 Troubleshooting

### Issue: "No crawled content found"
**Solution**: Run crawler first: `python federal_crawler.py`

### Issue: "Vector database not found"
**Solution**: Run processor and build: `python content_processor.py && python build_vector_db.py`

### Issue: "OpenAI API error"
**Solution**: Check API key: `echo $OPENAI_API_KEY`

### Issue: Out of memory
**Solution**: Process in smaller batches or increase RAM

---

## 📝 Files Summary

| File | Purpose |
|------|---------|
| `federal_crawler.py` | Web crawler |
| `content_processor.py` | Text processing |
| `build_vector_db.py` | Embedding generation |
| `query_service.py` | Search & AI service |
| `api_server.py` | REST API server |
| `requirements_complete.txt` | Dependencies |
| `deploy.sh` | Deployment script |
| `Dockerfile` | Container config |
| `docker-compose.yml` | Multi-container setup |
| `config.yaml` | System configuration |

---

## 🎓 Next Steps

1. **Test locally** with small dataset
2. **Deploy to cloud** for 24/7 access
3. **Integrate** with your existing workflows
4. **Monitor** and optimize performance
5. **Expand** to additional regulatory sources

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review system logs
3. Test with simple queries first
4. Verify all dependencies installed

---

**Version**: 1.0  
**Created**: October 29, 2025  
**Status**: Production-ready
