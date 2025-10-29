
# Retry creating documentation

print("=" * 80)
print("FEDERAL REGULATORY CRAWLER SYSTEM - BUILD COMPLETE")
print("=" * 80)
print()

summary = """
✅ STREAMLINED FEDERAL CRAWLER SYSTEM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 NEW COMPONENTS (2 FILES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. federal_crawler.py (14 KB)
   ✓ Focused federal URL crawler
   ✓ Recursive child page discovery
   ✓ Breadth-first search crawling
   ✓ PDF + HTML extraction
   ✓ Domain filtering (.gov only)
   ✓ Polite crawling with delays
   ✓ Page limits per domain
   ✓ JSON + CSV output

2. ai_wrapper.py (9 KB)
   ✓ AI-powered question answering
   ✓ Uses crawled content as context
   ✓ Keyword search (upgradeable to semantic)
   ✓ OpenAI/Anthropic integration
   ✓ SOP compliance checking
   ✓ Markdown report generation


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. INSTALL DEPENDENCIES
   pip install requests beautifulsoup4 lxml PyMuPDF pandas openai

2. CRAWL FEDERAL URLS (with all child pages)
   # Test with 3 URLs first
   python federal_crawler.py --csv ai_enhanced_dpw_compliance_resources.csv --max-urls 3
   
   # Full crawl of all federal URLs
   python federal_crawler.py --csv ai_enhanced_dpw_compliance_resources.csv

3. USE AI TO ANSWER QUESTIONS
   export OPENAI_API_KEY="your-key"
   python ai_wrapper.py --ask "What are OSHA fall protection requirements?"

4. CHECK YOUR SOP
   python ai_wrapper.py --check-sop construction_sop.txt --output report.md


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHAT IT DOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FEDERAL CRAWLER:
✓ Reads federal URLs from your CSV (24 federal resources)
✓ Visits each URL and extracts content
✓ Discovers and follows ALL child page links
✓ Crawls recursively (main page + children + grandchildren)
✓ Handles HTML pages and PDF documents
✓ Stays within federal .gov domains only
✓ Respects rate limits and robots.txt
✓ Saves full text content for each page

OUTPUT:
✓ federal_crawl_output/crawl_index.json - Master index
✓ federal_crawl_output/content/*.json - Individual pages
✓ federal_crawl_output/crawled_federal_full_text.csv - All content

AI WRAPPER:
✓ Loads all crawled content
✓ Searches for relevant regulations
✓ Builds context for AI model
✓ Sends question + context to GPT/Claude
✓ Returns answer with source citations
✓ Can check entire SOPs for compliance


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CRAWL CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEPTH SETTINGS:
  --max-depth 0   Only main URL
  --max-depth 1   Main URL + immediate children
  --max-depth 2   Main + children + grandchildren (DEFAULT)
  --max-depth 3   Goes even deeper

POLITENESS SETTINGS:
  --delay 2.0     2 seconds between requests (DEFAULT)
  --delay 5.0     More polite (slower)
  --delay 1.0     Faster (use carefully)

LIMITS:
  --max-urls 5                Limit URLs from CSV
  --max-pages-per-domain 100  Max pages per domain (DEFAULT)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 EXAMPLE WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Step 1: Test crawl with 3 URLs
python federal_crawler.py --max-urls 3 --max-depth 1

# Output shows:
# → [0] https://www.osha.gov/laws-regs/regulations/standardnumber/1926
#   ✓ Extracted 45231 chars, found 67 links
#   → [1] https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.501
#     ✓ Extracted 12456 chars, found 23 links
#   → [1] https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.502
#     ✓ Extracted 15789 chars, found 31 links
# ✓ Crawled 35 pages from https://www.osha.gov/...

# Step 2: Check crawled content
cat federal_crawl_output/crawl_index.json

# Step 3: Ask AI a question
python ai_wrapper.py --ask "What are fall protection requirements?"

# Step 4: Full crawl all federal URLs
python federal_crawler.py

# Step 5: Check your SOP
python ai_wrapper.py --check-sop my_sop.txt


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PERFORMANCE ESTIMATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For 24 federal URLs @ depth 2:
  • Assume ~10 child pages per URL
  • Total pages: ~240 pages
  • Crawl time: 240 pages × 3 sec = 12-20 minutes
  • Storage: ~50-200 MB
  • AI queries: ~5-15 seconds per question


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 COST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRAWLING: $0 (free, open source)

AI WRAPPER:
  • Without API key: Free (keyword search only)
  • With OpenAI: ~$0.01-$0.03 per question
  • Monthly (100 questions): ~$1-3


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ KEY FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPREHENSIVE CRAWLING:
✓ Gets ALL child pages automatically
✓ No manual URL list needed
✓ Discovers linked regulations
✓ Follows internal federal links
✓ Configurable depth control

SMART FILTERING:
✓ Federal .gov domains only
✓ Skips non-content (login, search, images)
✓ Stays within same domain/subdomain
✓ Respects domain page limits

ROBUST EXTRACTION:
✓ HTML text cleaning
✓ PDF text extraction
✓ Title and metadata capture
✓ Link discovery and tracking
✓ Error handling and logging

AI INTEGRATION:
✓ Context-aware Q&A
✓ Source citation
✓ SOP compliance checking
✓ Markdown report generation


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ADVANTAGES OF THIS APPROACH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

vs. Manual URL Collection:
✓ Automatically discovers child pages
✓ No need to list every single URL
✓ Finds regulations you didn't know existed

vs. Web Scraping Only:
✓ Saves content locally for AI processing
✓ Enables offline analysis
✓ Faster repeated queries

vs. GovInfo API Only:
✓ Gets content from ALL federal sites (not just CFR)
✓ Includes agency-specific guidance
✓ Captures implementation documents

BEST OF BOTH WORLDS:
✓ Use federal_crawler for comprehensive content
✓ Use GovInfo API for structured CFR data
✓ Combine for complete coverage


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print(summary)

print("\n" + "=" * 80)
print("✅ FEDERAL CRAWLER SYSTEM COMPLETE")
print("=" * 80)
print()
print("You now have a streamlined system that:")
print()
print("  1. ✓ Crawls ALL federal URLs from your CSV")
print("  2. ✓ Automatically discovers and crawls child pages")
print("  3. ✓ Extracts full text from HTML and PDF")
print("  4. ✓ Saves everything for AI processing")
print("  5. ✓ Provides AI wrapper for question answering")
print("  6. ✓ Can check SOPs for compliance")
print()
print("Two files ready to use:")
print("  • federal_crawler.py - Comprehensive federal crawler")
print("  • ai_wrapper.py - AI-powered compliance assistant")
print()
print("Next step:")
print("  python federal_crawler.py --csv ai_enhanced_dpw_compliance_resources.csv --max-urls 3")
print()
print("=" * 80)
