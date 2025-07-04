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


class StockAnalysisPipeline:
    def __init__(self, gemini_api_key):
        """Initialize the pipeline with configurations"""
        # Gemini setup
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

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

    def fetch_transcripts(self, stock_code, max_links=4):
        """Step 1: Scrape transcript links for a stock"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

        for stock_group in transcript_data:
            stock_name = stock_group[0]['Stock']
            print(f"\n📈 Analyzing keywords for: {stock_name}")

            file_cols = [f"File {i + 1}" for i in range(len(stock_group))]
            summary_table = pd.DataFrame(index=self.keywords, columns=file_cols).fillna("")

            for idx, transcript in enumerate(stock_group):
                url = transcript['URL']
                print(f"🌐 Fetching: {url}")

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

                    kw_matches = self.filter_keywords(full_text)
                    for kw, snippets in kw_matches.items():
                        preview = " | ".join(snippets)
                        if summary_table.loc[kw, file_cols[idx]]:
                            summary_table.loc[kw, file_cols[idx]] += " | " + preview
                        else:
                            summary_table.loc[kw, file_cols[idx]] = preview

                except Exception as e:
                    print(f"⚠️ Error fetching {url}: {e}")

            summary_table = summary_table.fillna("-")
            summary_table = summary_table.reset_index()
            summary_table["Stock"] = stock_name
            all_keyword_data.append(summary_table)

        return pd.concat(all_keyword_data, ignore_index=True) if all_keyword_data else pd.DataFrame()

    def generate_summaries(self, keyword_df):
        """Step 3: Generate summaries using Gemini"""
        summaries = []

        for stock in keyword_df["Stock"].unique():
            print(f"\n🤖 Generating summary for: {stock}")
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

            time.sleep(0.5)  # Normal delay

        return pd.DataFrame(summaries)

    def run_pipeline(self, max_docs_per_stock=4, save_intermediates=False):
        """Run the complete pipeline"""
        print("🚀 Starting Stock Analysis Pipeline...")
        print("=" * 50)

        # Step 1: Scrape transcript links
        print("\n📋 STEP 1: Scraping transcript links...")
        all_transcript_data = []

        for stock in self.selected_stock_list:
            transcript_links = self.fetch_transcripts(stock, max_docs_per_stock)
            if transcript_links:
                all_transcript_data.append(transcript_links)

        if not all_transcript_data:
            print("❌ No transcript links found. Exiting pipeline.")
            return None

        # Optional: Save transcript links
        if save_intermediates:
            all_links_df = pd.concat([pd.DataFrame(group) for group in all_transcript_data], ignore_index=True)
            all_links_df.to_excel("Pipeline_Transcripts.xlsx", index=False)
            print("💾 Transcript links saved to Pipeline_Transcripts.xlsx")

        # Step 2: Extract keywords
        print("\n🔍 STEP 2: Extracting keywords and context...")
        keyword_df = self.analyze_transcript_urls(all_transcript_data)

        if keyword_df.empty:
            print("❌ No keywords extracted. Exiting pipeline.")
            return None

        # Optional: Save keyword data
        if save_intermediates:
            keyword_df.to_csv("Pipeline_Keywords.csv", index=False)
            print("💾 Keyword data saved to Pipeline_Keywords.csv")

        # Step 3: Generate summaries
        print("\n🤖 STEP 3: Generating AI summaries...")
        summaries_df = self.generate_summaries(keyword_df)

        if summaries_df.empty:
            print("❌ No summaries generated. Exiting pipeline.")
            return None

        # Save final results
        summaries_df.to_csv("Pipeline_Final_Summaries.csv", index=False)
        print("\n✅ PIPELINE COMPLETED!")
        print("💾 Final summaries saved to Pipeline_Final_Summaries.csv")
        print("=" * 50)

        return summaries_df


def main():
    """Main function to run the pipeline"""
    # Configuration
    GEMINI_API_KEY = "AIzaSyCKAqLPFgidL7L32sUeCKmvggnh2C1AhTo"  # Replace with your API key

    # Get user input
    try:
        user_input = input("Enter number of recent documents to download for each stock (default is 4): ")
        max_docs = int(user_input.strip()) if user_input.strip().isdigit() else 4
    except:
        max_docs = 4

    save_intermediates = input("Save intermediate files? (y/n, default=n): ").lower().startswith('y')

    # Initialize and run pipeline
    pipeline = StockAnalysisPipeline(GEMINI_API_KEY)
    results = pipeline.run_pipeline(max_docs_per_stock=max_docs, save_intermediates=save_intermediates)

    if results is not None:
        print(f"\n📊 Pipeline Summary:")
        print(f"   • Stocks processed: {len(results)}")
        print(f"   • Documents per stock: {max_docs}")
        print(f"   • Final output: Pipeline_Final_Summaries.csv")

        # Show first few results
        print(f"\n📈 First 3 summaries:")
        for i, (_, row) in enumerate(results.head(3).iterrows()):
            print(f"   {i + 1}. {row['Stock']}: {row['Summary'][:100]}...")


if __name__ == "__main__":
    main()