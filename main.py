# Combined Stock Analysis Pipeline
# Combines: Link Scraping -> Keyword Extraction -> Gemini Summarization

import os
import time
import pandas as pd
import requests
import pdfplumber
from bs4 import BeautifulSoup
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import random
import glob
from tqdm import tqdm


class StockAnalysisPipeline:
    def __init__(self, gemini_api_keys):
        """Initialize the pipeline with configurations"""
        # API Key management - accept list of API keys
        if isinstance(gemini_api_keys, str):
            self.api_keys = [gemini_api_keys]
        else:
            self.api_keys = gemini_api_keys

        self.current_key_index = 0
        self.stocks_processed = 0
        self.stocks_per_key = 15

        # Initialize Gemini with first API key
        self._configure_gemini()

        # Load selected stocks
        self.selected_stocks_df = pd.read_excel("stock_list.xlsx")
        self.selected_stock_list = self.selected_stocks_df["Stock"].dropna().str.lower().unique()

        # Keywords for extraction
        self.keywords = [
            # Financial performance
            "revenue", "topline", "bottomline", "EBITDA", "EBIT", "PAT", "net profit",
            "gross margin", "margins", "operating leverage", "cost pressure", "input cost",
            "realization", "pricing power", "price hike", "discounting",

            # Costs & efficiency
            "raw material", "RM cost", "energy cost", "power cost", "gas prices",
            "opex", "cost optimization", "efficiency", "productivity", "cost leadership",

            # Capex & expansion
            "capex", "expansion", "capacity utilization", "commissioning",
            "greenfield", "brownfield", "debottlenecking", "backward integration",

            # Liquidity & balance sheet
            "free cash flow", "working capital", "cash conversion",
            "net debt", "debt reduction", "interest coverage", "leverage", "finance cost",
            "capital adequacy", "collections", "disbursement",

            # Ratios
            "ROCE", "ROE", "asset turnover", "inventory days", "receivable days", "payable days",

            # Business drivers
            "demand", "volume growth", "product mix", "premiumization",
            "channel mix", "SKU", "new launch", "market share",
            "domestic", "exports", "geo mix", "international business",

            # Seasonality & cycles
            "festive season", "wedding season", "monsoon",
            "seasonality", "inventory build-up", "destocking", "restocking", "inventory correction",

            # Macro & regulatory
            "headwinds", "tailwinds", "macro uncertainty", "regulatory environment",
            "GST", "budget impact", "PLI", "FAME", "subsidy", "tax rate", "duty impact", "customs",

            # Management tone & outlook
            "guidance", "outlook", "visibility", "confident", "cautious", "optimistic",
            "conservative", "hopeful", "strong growth", "muted", "rebound", "softness",
            "moderation", "volatility", "stability",

            # Supply chain & execution
            "supply chain", "logistics", "freight cost", "warehousing",
            "sourcing", "import substitution", "supply constraints", "project delays",

            # Corporate actions
            "promoter holding", "pledge", "buyback", "dividend payout", "shareholding",

            # Tech, ESG, innovation
            "AI adoption", "EV transition", "sustainability", "ESG", "carbon footprint",
            "green initiatives", "R&D", "innovation", "automation", "digital transformation",
            "cybersecurity", "cloud adoption", "patents", "benchmarking",

            # Workforce & delivery
            "attrition", "hiring", "utilization", "offshore", "onsite",
            "subcontracting", "bench", "billed effort"
        ]

        # Configuration
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        # System instruction for Gemini
        self.system_instruction = (
            "You are an equity research analyst. Based on the following keyword highlights across quarters, "
            "summarize the business performance, strategy, outlook, and risks. Be concise but insightful. "
            "Avoid disclaimers or narrative tone. Segregate each file in the pointers. "
            "Try to segregate quarters in each pointer."
        )

    def _configure_gemini(self):
        """Configure Gemini with current API key"""
        current_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        print(f"🔑 Using API key {self.current_key_index + 1}/{len(self.api_keys)}")

    def _check_and_rotate_key(self):
        """Check if need to rotate API key and rotate if necessary"""
        if self.stocks_processed > 0 and self.stocks_processed % self.stocks_per_key == 0:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self._configure_gemini()
            print(
                f"🔄 Rotated to API key {self.current_key_index + 1}/{len(self.api_keys)} after {self.stocks_processed} stocks")

    def fetch_transcripts(self, stock_code, max_links=4, driver=None):
        """Step 1: Scrape transcript links for a stock"""
        if driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver_created = True
        else:
            driver_created = False

        results = []

        try:
            driver.get(f"https://www.screener.in/company/{stock_code}/")
            time.sleep(2)

            try:
                doc_tab = driver.find_element(By.LINK_TEXT, "Documents")
                doc_tab.click()
                time.sleep(2)
            except:
                print(f"❌ Could not find 'Documents' tab for {stock_code}")
                return results

            print(f"🔍 Fetching transcripts for {stock_code}...")
            transcript_links = driver.find_elements(By.XPATH, '//a[contains(text(), "Transcript")]')

            if not transcript_links:
                print(f"❌ No transcript links found for {stock_code}.")
                return results

            for link in transcript_links[:max_links]:
                results.append({
                    "Stock": stock_code.upper(),
                    "Title": link.text.strip(),
                    "URL": link.get_attribute('href')
                })

            print(f"✅ {len(results)} transcripts found for {stock_code}")

        finally:
            if driver_created:
                driver.quit()

        return results

    def extract_text_from_pdf(self, url):
        """Extract text from PDF URL"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.get(url, timeout=10, verify=False, headers=self.headers)
                response.raise_for_status()
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)
                with pdfplumber.open("temp.pdf") as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    print(f"⚠️ Retry {attempt} for PDF failed. Retrying in {self.RETRY_DELAY}s...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"❌ Failed to fetch PDF after {self.MAX_RETRIES} attempts: {url} | Reason: {e}")
                    raise e

    def extract_keyword_context(self, text, keyword):
        """Extract context around keywords (50 words before and after)"""
        words = text.split()
        contexts = []
        for i, word in enumerate(words):
            if keyword in word.lower():
                start = max(i - 50, 0)
                end = min(i + 50, len(words))
                snippet = " ".join(words[start:end])
                contexts.append(snippet)
        return contexts

    def filter_keywords(self, text):
        """Filter and extract keyword contexts"""
        filtered = {}
        for kw in self.keywords:
            matches = self.extract_keyword_context(text.lower(), kw)
            if matches:
                print(f"🔍 Found keyword '{kw}' in: {matches[0][:100]}...")
                filtered[kw] = matches[:2]  # limit to first 2
        return filtered

    def analyze_transcript_urls(self, transcript_data):
        """Step 2: Extract keywords from transcript URLs"""
        all_keyword_data = []

        # Progress bar for analyzing transcript URLs
        pbar_stocks = tqdm(transcript_data, desc="📊 Analyzing stocks", unit="stock")

        for stock_group in pbar_stocks:
            stock_name = stock_group[0]['Stock']
            pbar_stocks.set_description(f"📊 Analyzing {stock_name}")

            file_cols = [f"File {i + 1}" for i in range(len(stock_group))]
            summary_table = pd.DataFrame(index=self.keywords, columns=file_cols).fillna("")

            # Progress bar for processing transcripts within each stock
            pbar_transcripts = tqdm(stock_group, desc=f"🌐 Processing {stock_name} transcripts",
                                    unit="transcript", leave=False)

            for idx, transcript in enumerate(pbar_transcripts):
                url = transcript['URL']
                pbar_transcripts.set_description(f"🌐 Fetching {stock_name} transcript {idx + 1}")

                try:
                    if url.endswith(".pdf"):
                        full_text = self.extract_text_from_pdf(url)
                    else:
                        for attempt in range(1, self.MAX_RETRIES + 1):
                            try:
                                response = requests.get(url, timeout=10, headers=self.headers)
                                response.raise_for_status()
                                break
                            except Exception as e:
                                if attempt < self.MAX_RETRIES:
                                    print(f"⚠️ Retry {attempt} for webpage failed. Retrying in {self.RETRY_DELAY}s...")
                                    time.sleep(self.RETRY_DELAY)
                                else:
                                    print(
                                        f"❌ Failed to fetch webpage after {self.MAX_RETRIES} attempts: {url} | Reason: {e}")
                                    raise e
                        soup = BeautifulSoup(response.text, 'html.parser')
                        full_text = soup.get_text(separator='\n')

                    print(f"📄 First 500 chars of text from {url}:")
                    print(full_text[:500])

                    # Progress bar for keyword filtering
                    kw_matches = {}
                    pbar_keywords = tqdm(self.keywords, desc=f"🔍 Filtering keywords for {stock_name}",
                                         unit="keyword", leave=False)

                    for kw in pbar_keywords:
                        pbar_keywords.set_description(f"🔍 Checking '{kw}' in {stock_name}")
                        matches = self.extract_keyword_context(full_text.lower(), kw)
                        if matches:
                            kw_matches[kw] = matches[:2]  # limit to first 2

                    pbar_keywords.close()

                    for kw, snippets in kw_matches.items():
                        preview = " | ".join(snippets)
                        if summary_table.loc[kw, file_cols[idx]]:
                            summary_table.loc[kw, file_cols[idx]] += " | " + preview
                        else:
                            summary_table.loc[kw, file_cols[idx]] = preview

                except Exception as e:
                    print(f"⚠️ Error fetching {url}: {e}")

            pbar_transcripts.close()

            summary_table = summary_table.fillna("-")
            summary_table = summary_table.reset_index()
            summary_table["Stock"] = stock_name
            all_keyword_data.append(summary_table)

        pbar_stocks.close()
        return pd.concat(all_keyword_data, ignore_index=True) if all_keyword_data else pd.DataFrame()

    def generate_summaries(self, keyword_df):
        """Step 3: Generate summaries using Gemini with API key rotation"""
        summaries = []
        unique_stocks = keyword_df["Stock"].unique()

        # Progress bar for generating summaries
        pbar_summaries = tqdm(unique_stocks, desc="🤖 Generating summaries", unit="stock")

        for stock in pbar_summaries:
            # Check and rotate API key if needed
            self._check_and_rotate_key()

            pbar_summaries.set_description(f"🤖 Generating summary for {stock}")
            stock_df = keyword_df[keyword_df["Stock"] == stock]

            # Create context from keywords and matching text
            keyword_info = ""
            for _, row in stock_df.iterrows():
                keyword = row["index"]
                text_fragments = [str(row[col]) for col in stock_df.columns if
                                  col.startswith("File") and pd.notna(row[col]) and row[col] != "-"]
                if text_fragments:
                    keyword_info += f"\n📌 {keyword}:\n" + "\n".join(text_fragments[:2]) + "\n"

            if not keyword_info.strip():
                continue

            prompt = f"{self.system_instruction}\n\nCompany: {stock}\n\nKeyword Notes:{keyword_info}"

            for attempt in range(2):  # Try at most 2 times
                try:
                    response = self.model.generate_content(prompt)
                    summaries.append({"Stock": stock, "Summary": response.text})
                    print(f"✅ Summary generated for {stock}")
                    break  # Successful, break out of retry loop
                except Exception as e:
                    print(f"⚠️ Error generating summary for {stock} on attempt {attempt + 1}: {e}")
                    if attempt == 0:
                        print("⏳ Waiting 10 seconds before retry...")
                        time.sleep(10)
                    else:
                        summaries.append({"Stock": stock, "Summary": f"ERROR: {e}"})

            # Increment stocks processed counter
            self.stocks_processed += 1
            time.sleep(0.5)  # Normal delay

        pbar_summaries.close()
        return pd.DataFrame(summaries)

    def run_pipeline(self, max_docs_per_stock=4, save_intermediates=False):
        """Run the complete pipeline"""
        print("🚀 Starting Stock Analysis Pipeline...")
        print(f"📊 Total API keys available: {len(self.api_keys)}")
        print(f"🔄 Will rotate every {self.stocks_per_key} stocks")
        print("=" * 50)

        # Step 1: Scrape transcript links in batches of 60
        print("\n📋 STEP 1: Scraping transcript links...")
        batch_size = 60
        temp_files = []

        # Progress bar for batches
        total_batches = (len(self.selected_stock_list) + batch_size - 1) // batch_size
        pbar_batches = tqdm(range(0, len(self.selected_stock_list), batch_size),
                            desc="📦 Processing batches", unit="batch", total=total_batches)

        for batch_start in pbar_batches:
            batch_stocks = self.selected_stock_list[batch_start: batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            pbar_batches.set_description(f"📦 Processing batch {batch_num}/{total_batches}")

            all_transcript_data = []
            # Use 3 browser tabs (drivers)
            drivers = [webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                        options=webdriver.ChromeOptions()) for _ in range(3)]

            # Progress bar for stocks within batch
            pbar_stocks = tqdm(batch_stocks, desc=f"🔄 Batch {batch_num} transcripts",
                               unit="stock", leave=False)

            for i, stock in enumerate(pbar_stocks):
                driver = drivers[i % 3]
                pbar_stocks.set_description(f"🔄 Fetching {stock} transcripts")
                try:
                    transcript_links = self.fetch_transcripts(stock, max_docs_per_stock, driver=driver)
                    if transcript_links:
                        all_transcript_data.append(transcript_links)
                    time.sleep(random.uniform(1.5, 2.2))  # Random delay to avoid being blocked
                except Exception as e:
                    print(f"⚠️ Error processing {stock}: {e}")

            pbar_stocks.close()

            for d in drivers:
                d.quit()

            if not all_transcript_data:
                print("❌ No transcript links found in this batch.")
                continue

            keyword_df = self.analyze_transcript_urls(all_transcript_data)
            if keyword_df.empty:
                print("❌ No keywords extracted in this batch.")
                continue

            summaries_df = self.generate_summaries(keyword_df)
            if summaries_df.empty:
                print("❌ No summaries generated in this batch.")
                continue

            temp_file = f"Pipeline_Temp_Summary_Batch_{batch_num}.csv"
            summaries_df.to_csv(temp_file, index=False)
            print(f"💾 Saved batch summary to {temp_file}")
            temp_files.append(temp_file)

        pbar_batches.close()

        # Combine all batch files
        if temp_files:
            print("\n📊 STEP 4: Combining batch results...")
            pbar_combine = tqdm(temp_files, desc="📊 Combining batch files", unit="file")

            combined_dfs = []
            for temp_file in pbar_combine:
                pbar_combine.set_description(f"📊 Reading {temp_file}")
                combined_dfs.append(pd.read_csv(temp_file))

            pbar_combine.close()

            combined_df = pd.concat(combined_dfs, ignore_index=True)
            combined_df.to_csv("Pipeline_Final_Summaries.csv", index=False)
            print("📊 Combined all batches into Pipeline_Final_Summaries.csv")

            # Clean up temporary files
            pbar_cleanup = tqdm(temp_files, desc="🧹 Cleaning up temp files", unit="file")
            for temp_file in pbar_cleanup:
                pbar_cleanup.set_description(f"🧹 Deleting {temp_file}")
                os.remove(temp_file)
            pbar_cleanup.close()
            print("🧹 Temporary batch files deleted.")

        return pd.read_csv("Pipeline_Final_Summaries.csv")


def main():
    """Main function to run the pipeline"""
    # Configuration - Add your 3 API keys here
    GEMINI_API_KEYS = [
        "AIzaSyCKAqLPFgidL7L32sUeCKmvggnh2C1AhTo",  # API Key 1
        "AIzaSyBS67gNUVyAY51L-_eurzfGzGLkG4m9r8Q",  # API Key 2
        "AIzaSyDQItObHG6C80KP1-0-ZyaGZehcvHPN4tY",  # API Key 3
        "AIzaSyB1G3JgPaBz1f3yI1oQwkA9oOxSzaWuU0w"  # API Key 4
    ]

    # Get user input
    try:
        user_input = input("Enter number of recent documents to download for each stock (default is 4): ")
        max_docs = int(user_input.strip()) if user_input.strip().isdigit() else 4
    except:
        max_docs = 4

    save_intermediates = input("Save intermediate files? (y/n, default=n): ").lower().startswith('y')

    # Initialize and run pipeline
    pipeline = StockAnalysisPipeline(GEMINI_API_KEYS)
    results = pipeline.run_pipeline(max_docs_per_stock=max_docs, save_intermediates=save_intermediates)

    if results is not None:
        print(f"\n📊 Pipeline Summary:")
        print(f"   • Stocks processed: {len(results)}")
        print(f"   • Documents per stock: {max_docs}")
        print(f"   • API keys rotated: Every {pipeline.stocks_per_key} stocks")
        print(f"   • Final output: Pipeline_Final_Summaries.csv")

        # Show first few results
        print(f"\n📈 First 3 summaries:")
        for i, (_, row) in enumerate(results.head(3).iterrows()):
            print(f"   {i + 1}. {row['Stock']}: {row['Summary'][:100]}...")


if __name__ == "__main__":
    main()
