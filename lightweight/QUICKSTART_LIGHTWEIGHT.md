# Lightweight RAG System - Quick Start Guide

## What This Is

A **single-file** regulatory compliance Q&A system that:
- Crawls federal regulatory websites
- Stores content in simple JSON format
- Searches using keyword + TF-IDF (no vector database needed)
- Answers questions with AI citations

## Key Advantages

✓ **Ultra Simple**: One Python file, 3 dependencies  
✓ **Fast Setup**: Install and run in 5 minutes  
✓ **No Heavy Dependencies**: No transformers, no FAISS, no pandas  
✓ **Low Memory**: Runs on 2GB RAM  
✓ **Portable**: Single JSON file contains all data  

## Installation

```bash
# Install minimal dependencies
pip install requests beautifulsoup4 openai

# That's it!
```

## Usage

### Step 1: Crawl Federal Regulatory Content

```bash
# Crawl 10 URLs from your CSV
python lightweight_rag.py --crawl federal_dpw_compliance_resources.csv --max-urls 10
```

This creates `regulatory_content.json` with all crawled data.

### Step 2: Ask Questions

```bash
# Ask a single question
python lightweight_rag.py --ask "What are OSHA fall protection requirements?"

# Interactive mode
python lightweight_rag.py
```

### Step 3: Use Without AI (Free)

```bash
# Keyword search only (no OpenAI needed)
python lightweight_rag.py --ask "Your question" --no-ai
```

## How It Works

1. **Crawling**: Fetches HTML from URLs, extracts text  
2. **Storage**: Saves everything in `regulatory_content.json`  
3. **Search**: Simple keyword matching + TF-IDF scoring  
4. **AI Answer**: Sends top results to GPT-4 as context  
5. **Citations**: Returns answer with source URLs  

## Performance

- **Crawl 10 URLs**: ~1-2 minutes  
- **Search**: <100ms (instant)  
- **AI Answer**: 2-5 seconds  
- **Memory**: ~50-200 MB  
- **Storage**: 1-10 MB JSON file  

## Cost

- **Crawling & Search**: $0 (free)  
- **AI Answers**: ~$0.01-0.03 per question  
- **Total**: ~$1-3/month for 100 questions  

## Comparison to Full System

| Feature | Full RAG | Lightweight |
|---------|----------|-------------|
| Files | 11 files | **1 file** |
| Dependencies | 15+ packages | **3 packages** |
| Setup time | 2-4 hours | **5 minutes** |
| Memory | 8GB+ | **2GB** |
| Storage | 500MB-1GB | **10MB** |
| Search method | Vector similarity | **Keyword + TF-IDF** |
| Accuracy | Very high | **Good** |
| Speed | Very fast | **Fast enough** |

## When to Use

**Use Lightweight RAG if**:
- You want simple and fast setup  
- You have <100 URLs to crawl  
- You don't need ultra-precise semantic search  
- You want to run on limited resources  

**Use Full RAG if**:
- You need maximum precision  
- You have 1000+ URLs to process  
- You need semantic similarity search  
- You want to scale to many users  

## Example Session

```bash
# Crawl content
$ python lightweight_rag.py --crawl federal_dpw_compliance_resources.csv --max-urls 5
Loading URLs from federal_dpw_compliance_resources.csv...
Crawling 5 URLs...
[1/5] https://www.osha.gov/laws-regs...
[2/5] https://www.epa.gov/...
✓ Crawled 5 documents
✓ Saved 5 documents to regulatory_content.json

# Ask question
$ python lightweight_rag.py --ask "What are OSHA requirements for scaffolding?"

Searching for: What are OSHA requirements for scaffolding?

================================================================================
ANSWER
================================================================================
Based on the OSHA regulations, scaffolding requirements include:

1. Platforms must be fully planked
2. Guardrails required at heights above 10 feet
3. Fall protection for workers
4. Proper load capacity
5. Regular inspections

[Detailed AI-generated answer with specific citations...]

================================================================================
SOURCES
================================================================================

1. OSHA Construction Standards - 1926.451
   URL: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.451
   Score: 45

2. OSHA Scaffolding Safety Guide
   URL: https://www.osha.gov/scaffolding
   Score: 32
================================================================================
```

## Tips

1. **Start small**: Crawl 5-10 URLs first to test  
2. **Use --no-ai**: Test search without OpenAI costs  
3. **Save regularly**: Your data is in one JSON file  
4. **Re-crawl weekly**: Keep content up-to-date  

## Limitations

- Simple keyword search (not semantic)  
- No change detection  
- No vector database  
- Limited to ~1000 documents before slowing down  

## Upgrading

If you need more power later, you can:
1. Export your JSON to the full RAG system  
2. All your crawled content is preserved  
3. Get vector search and better accuracy  

---

**Perfect for**: Quick prototypes, small projects, learning RAG concepts  
**Ready in**: 5 minutes  
**Cost**: $0-3/month
