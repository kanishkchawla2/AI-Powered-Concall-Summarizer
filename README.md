# Stock Analysis Pipeline 📊

A comprehensive Python-based pipeline that automates the process of gathering, analyzing, and summarizing stock earnings call transcripts using AI-powered insights.

## 🚀 Features

- **Automated Web Scraping**: Extracts earnings call transcripts from Screener.in
- **Smart Keyword Extraction**: Identifies 80+ financial keywords with contextual analysis
- **AI-Powered Summarization**: Uses Google's Gemini AI to generate insightful business summaries
- **Batch Processing**: Handles large stock lists efficiently with progress tracking
- **API Key Rotation**: Automatically rotates between multiple Gemini API keys to handle rate limits
- **Robust Error Handling**: Includes retry mechanisms and fallback strategies

## 📋 Prerequisites

### Required Python Packages

```bash
pip install pandas requests pdfplumber beautifulsoup4 selenium webdriver-manager google-generativeai tqdm openpyxl urllib3
```

### Additional Requirements

- **Chrome Browser**: Required for Selenium web scraping
- **ChromeDriver**: Automatically managed by webdriver-manager
- **Google Gemini API Keys**: Minimum 1 key required (4 keys recommended for better performance)

## 📁 Project Structure

```
stock-analysis-pipeline/
├── main.py                    # Main pipeline script
├── stock_list.xlsx           # Excel file containing stock symbols
├── Pipeline_Final_Summaries.csv  # Final output file
└── README.md                 # This file
```

## 🛠️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd stock-analysis-pipeline
pip install -r requirements.txt
```

### 2. Prepare Stock List

Create a file named `stock_list.xlsx` with the following structure:

| Stock |
|-------|
| RELIANCE |
| TCS |
| INFY |
| HDFCBANK |
| ... |

### 3. Configure API Keys

Edit the `GEMINI_API_KEYS` list in the `main()` function:

```python
GEMINI_API_KEYS = [
    "your_first_api_key_here",
    "your_second_api_key_here",
    "your_third_api_key_here",
    "your_fourth_api_key_here"
]
```

**How to get Gemini API Keys:**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key to your configuration

### 4. Run the Pipeline

```bash
python main.py
```

## 🎯 How It Works

### Phase 1: Web Scraping 🌐
- Navigates to Screener.in for each stock
- Extracts earnings call transcript links
- Processes stocks in batches of 60 for efficiency

### Phase 2: Content Extraction 📄
- Downloads PDF transcripts or scrapes web pages
- Extracts full text content from documents
- Handles various document formats automatically

### Phase 3: Keyword Analysis 🔍
- Searches for 80+ predefined financial keywords
- Extracts contextual snippets (±50 words around keywords)
- Organizes findings by stock and document

### Phase 4: AI Summarization 🤖
- Uses Google's Gemini AI to analyze keyword contexts
- Generates concise business performance summaries
- Automatically rotates API keys to handle rate limits

## 📊 Key Financial Keywords Tracked

### Financial Performance
- Revenue, EBITDA, PAT, margins, pricing power
- Cost pressures, input costs, operating leverage

### Business Metrics
- Capacity utilization, volume growth, market share
- Demand patterns, product mix, channel mix

### Financial Health
- Free cash flow, working capital, debt levels
- ROCE, ROE, liquidity ratios

### Strategic Insights
- Expansion plans, capex, acquisitions
- Management guidance, outlook, risks

### Market Dynamics
- Seasonality, macro trends, regulatory changes
- Supply chain, competition, innovation

## 🔧 Configuration Options

### Pipeline Parameters

```python
# Number of recent documents per stock (default: 4)
max_docs_per_stock = 4

# Save intermediate files (default: False)
save_intermediates = False

# Stocks processed before API key rotation (default: 15)
stocks_per_key = 15

# Batch size for processing (default: 60)
batch_size = 60
```

### Advanced Settings

```python
# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5

# Context extraction (words around keywords)
context_window = 50

# Rate limiting delays
request_delay = (1.5, 2.2)  # Random delay range
```

## 📈 Output Format

The pipeline generates `Pipeline_Final_Summaries.csv` with:

| Stock | Summary |
|-------|---------|
| RELIANCE | Strong revenue growth driven by retail expansion... |
| TCS | Robust demand in BFSI vertical, margin expansion... |
| INFY | Digital transformation deals, large deal momentum... |

## 🚨 Common Issues & Solutions

### Issue: ChromeDriver Not Found
**Solution**: The script uses webdriver-manager to automatically download ChromeDriver. Ensure Chrome browser is installed.

### Issue: API Rate Limit Exceeded
**Solution**: Add more API keys to the `GEMINI_API_KEYS` list or reduce `stocks_per_key` value.

### Issue: PDF Extraction Fails
**Solution**: Some PDFs may be password-protected or corrupted. The script will log these failures and continue.

### Issue: Website Blocking
**Solution**: The script includes random delays and user-agent headers to avoid detection. Consider increasing delays if needed.

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **Rate Limits**: Respect API provider's rate limits
- **Web Scraping**: Follow robots.txt and terms of service
- **Data Privacy**: Ensure compliance with data protection regulations

## 🎛️ Customization Options

### Adding New Keywords
```python
# Add to the keywords list in __init__
self.keywords.extend([
    "your_custom_keyword_1",
    "your_custom_keyword_2"
])
```

### Modifying AI Prompt
```python
# Customize the system instruction
self.system_instruction = """
Your custom instruction for the AI model...
"""
```

### Changing Data Sources
```python
# Modify the fetch_transcripts method to use different websites
def fetch_transcripts(self, stock_code, max_links=4, driver=None):
    # Your custom scraping logic
    pass
```

## 📊 Performance Metrics

- **Processing Speed**: ~20-30 stocks per hour (depends on document count)
- **API Efficiency**: Automatic key rotation prevents rate limit issues
- **Memory Usage**: Processes in batches to maintain low memory footprint
- **Error Recovery**: Robust retry mechanisms ensure high success rates

## 🛡️ Error Handling

The pipeline includes comprehensive error handling:

- **Network Timeouts**: Automatic retries with exponential backoff
- **PDF Processing**: Graceful handling of corrupted files
- **API Failures**: Fallback mechanisms and error logging
- **Web Scraping**: Anti-detection measures and retry logic

## 🔄 Maintenance

### Regular Updates Needed
- Update ChromeDriver compatibility
- Monitor API key usage and billing
- Review and update financial keywords
- Check website structure changes

### Performance Optimization
- Adjust batch sizes based on system resources
- Optimize API key rotation frequency
- Fine-tune retry mechanisms
- Monitor processing speeds

## 📞 Support

For issues or questions:
1. Check the error logs in console output
2. Verify all prerequisites are installed
3. Ensure API keys are valid and have sufficient quota
4. Review the stock_list.xlsx format

## 📄 License

This project is intended for educational and research purposes. Please ensure compliance with:
- Website terms of service
- API usage policies
- Data protection regulations
- Financial data usage guidelines

---

**⚠️ Disclaimer**: This tool is for research and educational purposes only. Always verify financial data independently and consult with qualified professionals for investment decisions.
