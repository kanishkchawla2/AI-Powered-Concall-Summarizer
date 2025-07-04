# AI-Powered Concall Summarizer

Automates the analysis of stock earnings call transcripts using web scraping, keyword extraction, and AI-powered summarization.

## Overview

This tool combines three key components:
1. **Web Scraping**: Automatically fetches earnings call transcript links from Screener.in
2. **Keyword Extraction**: Extracts relevant financial keywords and context from transcripts
3. **AI Summarization**: Uses Google's Gemini API to generate business insights and summaries

## About Screener.in

[Screener.in](https://www.screener.in/) is a comprehensive stock analysis platform that provides:
- **Financial Data**: Balance sheets, profit & loss statements, cash flow statements
- **Stock Screeners**: Filter stocks based on various financial metrics
- **Company Documents**: Annual reports, quarterly results, and earnings call transcripts
- **Analysis Tools**: Ratios, peer comparisons, and historical performance data

This tool specifically leverages Screener.in's document repository to access earnings call transcripts, which contain valuable insights from company management about business performance, strategy, and outlook.

## Features

- Automated transcript discovery and download
- Contextual keyword extraction (50 words before/after each keyword)
- AI-powered business analysis and summarization
- Support for both PDF and web-based transcripts
- Configurable number of documents per stock
- Optional intermediate file saving for debugging

## System Requirements

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- Google Gemini API key
- Excel file with stock list (`stock_list.xlsx`)

## Setup

1. **Install Dependencies**
   ```bash
   pip install pandas requests pdfplumber beautifulsoup4 urllib3 selenium webdriver-manager google-generativeai openpyxl
   ```

2. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Replace the API key in the code

3. **Prepare Stock List**
   - Create `stock_list.xlsx` with a column named "Stock"
   - Add stock codes (e.g., "RELIANCE", "TCS", "INFY")

## Usage

### Basic Usage
```bash
python stock_analysis_pipeline.py
```

### Interactive Options
- **Number of documents**: Choose how many recent transcripts to analyze per stock (default: 4)
- **Save intermediates**: Option to save keyword extraction results for debugging

## Output Files

1. **Pipeline_Final_Summaries.csv**: Main output with AI-generated business summaries
2. **Pipeline_Keywords.csv**: Intermediate keyword extraction results (optional)
3. **Pipeline_Transcripts.xlsx**: Scraped transcript links (optional)

## Keyword Categories

The tool extracts context around 80+ financial keywords including:
- **Financial Performance**: Revenue, EBITDA, margins, profitability
- **Costs & Efficiency**: Raw material costs, operational expenses
- **Growth & Expansion**: Capex, capacity utilization, market share
- **Balance Sheet**: Cash flow, debt, working capital
- **Market Dynamics**: Demand, seasonality, regulatory changes
- **Management Outlook**: Guidance, confidence levels, risks

## Technical Details

### Web Scraping
- Uses Selenium WebDriver for dynamic content
- Handles both PDF and HTML transcript formats
- Implements retry logic with exponential backoff
- Respects website rate limits

### Keyword Extraction
- Context-aware extraction (±50 words around keywords)
- Handles multiple occurrences per document
- Filters relevant financial terminology

### AI Summarization
- Uses Google Gemini 2.5 Flash model
- Structured prompts for consistent output
- Error handling and retry mechanisms

## Limitations

- **Data Source**: Limited to Screener.in transcript availability
- **Rate Limits**: Subject to API and website rate limiting
- **Accuracy**: AI summaries should be verified for investment decisions

## Sample Output

```
Stock: RELIANCE
Summary: Strong revenue growth driven by retail expansion and digital initiatives. 
EBITDA margins improved due to operational efficiency gains. Management expressed 
confidence in petrochemical demand recovery. Key risks include crude oil volatility 
and regulatory changes in telecom sector...
```

## Error Handling

The pipeline includes robust error handling for:
- Network timeouts and connection issues
- PDF parsing failures
- API rate limiting
- Missing or malformed data

## Contributing

For improvements:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## Disclaimer

This tool is for educational purposes only. The financial analysis provided should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors and conduct thorough due diligence.

## License

MIT License - See LICENSE file for details

## Support

For questions or issues:
- Check the error logs in the console output
- Verify API key validity
- Ensure all dependencies are installed
- Check internet connectivity for web scraping

---

**Note**: Use responsibly and in compliance with website terms of service.
