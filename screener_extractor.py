# Screener Data Extractor
# Handles web scraping from screener.in and document processing

import time
import requests
import pdfplumber
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
from config import Config


class ScreenerExtractor:
    def __init__(self, max_retries=None, retry_delay=None):
        """Initialize the screener extractor with configuration"""
        self.MAX_RETRIES = max_retries or Config.MAX_RETRIES
        self.RETRY_DELAY = retry_delay or Config.RETRY_DELAY
        self.headers = {
            "User-Agent": Config.get_user_agent()
        }
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def create_driver(self, headless=True):
        """Create a Chrome WebDriver instance"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        return driver
    
    def fetch_transcript_links(self, stock_code, max_links=4, driver=None):
        """Fetch transcript links for a stock from screener.in"""
        driver_created = False
        if driver is None:
            driver = self.create_driver()
            driver_created = True
        
        results = []
        
        try:
            url = f"https://www.screener.in/company/{stock_code}/"
            print(f"🔗 Accessing: {url}")
            driver.get(url)
            time.sleep(2)
            
            try:
                doc_tab = driver.find_element(By.LINK_TEXT, "Documents")
                doc_tab.click()
                time.sleep(2)
                print(f"📂 Opened Documents tab for {stock_code}")
            except Exception as e:
                print(f"❌ Could not find 'Documents' tab for {stock_code}: {e}")
                return results
            
            print(f"🔍 Searching for transcripts for {stock_code}...")
            transcript_links = driver.find_elements(By.XPATH, '//a[contains(text(), "Transcript")]')
            
            if not transcript_links:
                print(f"❌ No transcript links found for {stock_code}")
                return results
            
            for link in transcript_links[:max_links]:
                results.append({
                    "Stock": stock_code.upper(),
                    "Title": link.text.strip(),
                    "URL": link.get_attribute('href')
                })
            
            print(f"✅ Found {len(results)} transcripts for {stock_code}")
            
        except Exception as e:
            print(f"❌ Error fetching transcripts for {stock_code}: {e}")
        finally:
            if driver_created:
                driver.quit()
        
        return results
    
    def extract_text_from_pdf(self, url):
        """Extract text from PDF URL"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                print(f"📄 Downloading PDF: {url}")
                response = requests.get(url, timeout=10, verify=False, headers=self.headers)
                response.raise_for_status()
                
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)
                
                with pdfplumber.open("temp.pdf") as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    print(f"✅ Extracted {len(text)} characters from PDF")
                    return text
                    
            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    print(f"⚠️ PDF extraction attempt {attempt} failed. Retrying in {self.RETRY_DELAY}s...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"❌ Failed to extract PDF after {self.MAX_RETRIES} attempts: {url} | Error: {e}")
                    raise e
    
    def extract_text_from_webpage(self, url):
        """Extract text from a webpage"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                print(f"🌐 Fetching webpage: {url}")
                response = requests.get(url, timeout=10, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator='\n')
                print(f"✅ Extracted {len(text)} characters from webpage")
                return text
                
            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    print(f"⚠️ Webpage extraction attempt {attempt} failed. Retrying in {self.RETRY_DELAY}s...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"❌ Failed to extract webpage after {self.MAX_RETRIES} attempts: {url} | Error: {e}")
                    raise e
    
    def extract_text_from_url(self, url):
        """Extract text from URL (auto-detect PDF or webpage)"""
        try:
            if url.endswith(".pdf"):
                return self.extract_text_from_pdf(url)
            else:
                return self.extract_text_from_webpage(url)
        except Exception as e:
            print(f"⚠️ Error extracting from {url}: {e}")
            return ""
    
    def batch_fetch_transcripts(self, stock_list, max_docs_per_stock=None, concurrent_drivers=None):
        """Fetch transcripts for multiple stocks with concurrent drivers"""
        if max_docs_per_stock is None:
            max_docs_per_stock = Config.DEFAULT_DOCS_PER_STOCK
        if concurrent_drivers is None:
            concurrent_drivers = Config.CONCURRENT_DRIVERS
            
        all_transcript_data = []
        
        # Create multiple drivers for concurrent processing
        drivers = [self.create_driver() for _ in range(concurrent_drivers)]
        
        try:
            for i, stock in enumerate(stock_list):
                driver = drivers[i % concurrent_drivers]
                print(f"🔄 Processing {stock} (Driver {(i % concurrent_drivers) + 1})")
                
                try:
                    transcript_links = self.fetch_transcript_links(
                        stock, max_docs_per_stock, driver=driver
                    )
                    if transcript_links:
                        all_transcript_data.append(transcript_links)
                    
                    # Random delay to avoid being blocked
                    time.sleep(random.uniform(1.5, 2.2))
                    
                except Exception as e:
                    print(f"⚠️ Error processing {stock}: {e}")
                    continue
        
        finally:
            # Clean up drivers
            for driver in drivers:
                try:
                    driver.quit()
                except:
                    pass
        
        return all_transcript_data
    
    def get_extractor_stats(self):
        """Get extractor configuration stats"""
        return {
            "max_retries": self.MAX_RETRIES,
            "retry_delay": self.RETRY_DELAY,
            "user_agent": self.headers["User-Agent"][:50] + "..."
        }
