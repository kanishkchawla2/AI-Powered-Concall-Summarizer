# Gemini AI Manager
# Handles all Gemini API interactions and summarization

import google.generativeai as genai
import time
from config import Config


class GeminiManager:
    def __init__(self, api_keys=None, stocks_per_key=None):
        """Initialize Gemini with API key rotation"""
        # Use config values if not provided
        if api_keys is None:
            self.api_keys = Config.GEMINI_API_KEYS
        else:
            if isinstance(api_keys, str):
                self.api_keys = [api_keys]
            else:
                self.api_keys = api_keys
        
        self.current_key_index = 0
        self.stocks_processed = 0
        self.stocks_per_key = stocks_per_key or Config.STOCKS_PER_API_KEY
        
        # Configure initial API key
        self._configure_gemini()
        
        # Use system instruction from config
        self.system_instruction = Config.SYSTEM_INSTRUCTION
    
    def _configure_gemini(self):
        """Configure Gemini with current API key"""
        current_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        print(f"🔑 Using API key {self.current_key_index + 1}/{len(self.api_keys)}")
    
    def _check_and_rotate_key(self):
        """Check if need to rotate API key and rotate if necessary"""
        if self.stocks_processed > 0 and self.stocks_processed % self.stocks_per_key == 0:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self._configure_gemini()
            print(f"🔄 Rotated to API key {self.current_key_index + 1}/{len(self.api_keys)} after {self.stocks_processed} stocks")
    
    def generate_summary(self, stock, keyword_info, max_retries=2):
        """Generate summary for a single stock"""
        # Check and rotate API key if needed
        self._check_and_rotate_key()
        
        if not keyword_info.strip():
            print(f"⚠️ No keyword info found for {stock}")
            return None
        
        prompt = f"{self.system_instruction}\n\nCompany: {stock}\n\nKeyword Notes:{keyword_info}"
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                print(f"✅ Summary generated for {stock}")
                self.stocks_processed += 1
                time.sleep(Config.GENERATION_DELAY)  # Use config delay
                return response.text
            except Exception as e:
                print(f"⚠️ Error generating summary for {stock} on attempt {attempt + 1}: {e}")
                if attempt == 0:
                    print(f"⏳ Waiting {Config.RETRY_DELAY} seconds before retry...")
                    time.sleep(Config.RETRY_DELAY)
                else:
                    print(f"❌ Failed to generate summary for {stock} after {max_retries} attempts")
                    return f"ERROR: {e}"
    
    def update_system_instruction(self, new_instruction):
        """Update the system instruction for Gemini"""
        self.system_instruction = new_instruction
        print("✅ System instruction updated")
    
    def get_api_usage_stats(self):
        """Get API usage statistics"""
        return {
            "total_keys": len(self.api_keys),
            "current_key": self.current_key_index + 1,
            "stocks_processed": self.stocks_processed,
            "stocks_per_key": self.stocks_per_key
        }
    
    def test_api_connection(self):
        """Test if the current API key is working"""
        try:
            test_response = self.model.generate_content("Test message")
            print("✅ Gemini API connection successful")
            return True
        except Exception as e:
            print(f"❌ Gemini API connection failed: {e}")
            return False
