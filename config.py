# Configuration Manager
# Handles all configuration settings for the pipeline

import os

class Config:
    """Configuration settings for the Stock Analysis Pipeline"""
    
    # Gemini API Keys (set directly here)
    # Example: ["your-gemini-key-1", "your-gemini-key-2"]
    GEMINI_API_KEYS = [
        "your-gemini-api-key-1",
        "your-gemini-api-key-2"
    ]
    
    # File paths
    STOCK_LIST_FILE = "stock_list.xlsx"
    SUBSET_STOCK_LIST_FILE = "subset_stock_list.xlsx"
    FINAL_OUTPUT_FILE = "Pipeline_Final_Summaries.csv"
    TEMP_FOLDER = "temp"
    TEMP_FILE_PREFIX = "temp/Pipeline_Temp_Summary_Batch_"
    
    # Pipeline settings
    DEFAULT_DOCS_PER_STOCK = 4
    DEFAULT_BATCH_SIZE = 60
    STOCKS_PER_API_KEY = 15
    
    # Web scraping settings
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    CONCURRENT_DRIVERS = 3
    
    # Keyword extraction settings
    CONTEXT_WORDS = 50  # Words before and after keyword
    MAX_MATCHES_PER_KEYWORD = 2
    
    # Gemini settings
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    GENERATION_DELAY = 0.5  # Seconds between API calls
    
    # System instruction for Gemini
    SYSTEM_INSTRUCTION = (
    "You are an equity research analyst. Based on the provided concall transcripts or keyword-level highlights "
    "across multiple quarters, produce a structured, standardized research summary. "
    "Summarize business performance, operational trends, financial metrics, strategy updates, management guidance, "
    "energy/sustainability initiatives, capex and leverage, and key risks. "
    "Be concise, analytical, and insight-driven. Avoid filler narrative or disclaimers. "
    "Present the output in clear pointer-wise sections. "
    "If multiple quarters are provided, aggregate insights across quarters within each pointer (do not repeat quarter-wise). "
    "Prioritize: utilization, realizations/pricing, margins, capacity, guidance, capex, debt trajectory, accounting changes, "
    "market commentary, export/domestic mix, demand trends, and risks. "
    "Where management quotes are impactful, include them in short verbatim form (<20 words). "
    "Ensure the final output is standardized in the following order: "
    "1) Executive Summary, 2) Performance & Financials, 3) Operations & Utilization, "
    "4) Pricing & Markets, 5) Energy & Sustainability, 6) Capex & Leverage, "
    "7) Management Guidance & Outlook, 8) Risks & Watch Items. "
    "Keep the tone factual, neutral, and research-oriented."
)

    
    @classmethod
    def get_user_agent(cls):
        """Get user agent string for web requests"""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        issues = []
        
        if not cls.GEMINI_API_KEYS or all(not str(key).strip() for key in cls.GEMINI_API_KEYS):
            issues.append("No valid Gemini API keys configured")
        
        if cls.DEFAULT_BATCH_SIZE <= 0:
            issues.append("Batch size must be positive")
        
        if cls.STOCKS_PER_API_KEY <= 0:
            issues.append("Stocks per API key must be positive")
        
        if cls.MAX_RETRIES <= 0:
            issues.append("Max retries must be positive")
        
        return issues
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("📋 CURRENT CONFIGURATION")
        print("-" * 40)
        print(f"   • API Keys: {len(cls.GEMINI_API_KEYS)} configured")
        print(f"   • Stock list file: {cls.STOCK_LIST_FILE}")
        print(f"   • Subset stock list file: {cls.SUBSET_STOCK_LIST_FILE}")
        print(f"   • Default docs per stock: {cls.DEFAULT_DOCS_PER_STOCK}")
        print(f"   • Default batch size: {cls.DEFAULT_BATCH_SIZE}")
        print(f"   • Stocks per API key: {cls.STOCKS_PER_API_KEY}")
        print(f"   • Max retries: {cls.MAX_RETRIES}")
        print(f"   • Concurrent drivers: {cls.CONCURRENT_DRIVERS}")
        print(f"   • Gemini model: {cls.GEMINI_MODEL}")
        
        # Validate configuration
        issues = cls.validate_config()
        if issues:
            print(f"\n⚠️  CONFIGURATION ISSUES:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ Configuration is valid")
