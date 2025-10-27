# Configuration Manager
# Handles all configuration settings for the pipeline

class Config:
    """Configuration settings for the Stock Analysis Pipeline"""
    
    # Gemini API Keys - Add your keys here
    GEMINI_API_KEYS = [
       "YOUR-API-KEY1", "YOUR-API-KEY2"
    ]
    
    # File paths
    STOCK_LIST_FILE = "stock_list.xlsx"
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
    GEMINI_MODEL = "gemini-2.5-flash-lite-preview-06-17"
    GENERATION_DELAY = 0.5  # Seconds between API calls
    
    # System instruction for Gemini
    SYSTEM_INSTRUCTION = (
        "You are an equity research analyst. Based on the following keyword highlights across quarters, "
        "summarize the business performance, strategy, outlook, and risks. Be concise but insightful. "
        "Avoid disclaimers or narrative tone. Segregate each file in the pointers. "
        "Try to gregate quarters in each pointer."
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
        
        if not cls.GEMINI_API_KEYS or all(not key.strip() for key in cls.GEMINI_API_KEYS):
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
