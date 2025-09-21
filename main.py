# Combined Stock Analysis Pipeline - Main Orchestrator
# Coordinates: Data Management -> Web Scraping -> Keyword Extraction -> AI Summarization

import os
import time
import pandas as pd
from tqdm import tqdm

# Import our custom modules
from data_manager import DataManager
from keywords_manager import KeywordsManager
from screener_extractor import ScreenerExtractor
from gemini_manager import GeminiManager
from config import Config


class StockAnalysisPipeline:
    def __init__(self, gemini_api_keys=None, stock_list_file=None):
        """Initialize the pipeline with all components"""
        print("🚀 Initializing Stock Analysis Pipeline...")
        
        # Use config values if not provided
        api_keys = gemini_api_keys or Config.GEMINI_API_KEYS
        stock_file = stock_list_file or Config.STOCK_LIST_FILE
        
        # Initialize all managers
        self.data_manager = DataManager(stock_file)
        self.keywords_manager = KeywordsManager()
        self.screener_extractor = ScreenerExtractor()
        self.gemini_manager = GeminiManager(api_keys)
        
        print("✅ All components initialized successfully")
    
    def analyze_transcript_urls(self, transcript_data):
        """Step 2: Extract keywords from transcript URLs"""
        all_keyword_data = []
        keywords = self.keywords_manager.get_keywords()
        
        # Progress bar for analyzing transcript URLs
        pbar_stocks = tqdm(transcript_data, desc="📊 Analyzing stocks", unit="stock")
        
        for stock_group in pbar_stocks:
            stock_name = stock_group[0]['Stock']
            pbar_stocks.set_description(f"📊 Analyzing {stock_name}")
            
            file_cols = [f"File {i + 1}" for i in range(len(stock_group))]
            summary_table = pd.DataFrame(index=keywords, columns=file_cols).fillna("")
            
            # Progress bar for processing transcripts within each stock
            pbar_transcripts = tqdm(stock_group, desc=f"🌐 Processing {stock_name} transcripts",
                                    unit="transcript", leave=False)
            
            for idx, transcript in enumerate(pbar_transcripts):
                url = transcript['URL']
                pbar_transcripts.set_description(f"🌐 Fetching {stock_name} transcript {idx + 1}")
                
                try:
                    # Extract text from URL
                    full_text = self.screener_extractor.extract_text_from_url(url)
                    
                    if full_text:
                        print(f"📄 First 500 chars of text from {url}:")
                        print(full_text[:500])
                        
                        # Extract keywords using keywords manager
                        kw_matches = self.keywords_manager.filter_keywords(full_text.lower())
                        
                        # Store keyword matches in summary table
                        for kw, snippets in kw_matches.items():
                            preview = " | ".join(snippets)
                            current_val = summary_table.loc[kw, file_cols[idx]]
                            if pd.notna(current_val) and str(current_val).strip():
                                summary_table.loc[kw, file_cols[idx]] = str(current_val) + " | " + preview
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
            pbar_summaries.set_description(f"🤖 Generating summary for {stock}")
            stock_df = keyword_df[keyword_df["Stock"] == stock]
            
            # Create context from keywords and matching text
            keyword_info = ""
            for _, row in stock_df.iterrows():
                keyword = row["index"]
                text_fragments = []
                for col in stock_df.columns:
                    if col.startswith("File"):
                        val = row[col]
                        if pd.notna(val) and str(val) != "-" and str(val).strip():
                            text_fragments.append(str(val))
                
                if text_fragments:
                    keyword_info += f"\n📌 {keyword}:\n" + "\n".join(text_fragments[:2]) + "\n"
            
            # Generate summary using Gemini manager
            summary = self.gemini_manager.generate_summary(stock, keyword_info)
            if summary:
                summaries.append({"Stock": stock, "Summary": summary})
        
        pbar_summaries.close()
        return pd.DataFrame(summaries)
    
    def run_pipeline(self, max_docs_per_stock=None, save_intermediates=False, batch_size=None):
        """Main pipeline execution with configurable parameters"""
        # Use config defaults if not provided
        max_docs_per_stock = max_docs_per_stock or Config.DEFAULT_DOCS_PER_STOCK
        batch_size = batch_size or Config.DEFAULT_BATCH_SIZE
        print("🚀 Starting Stock Analysis Pipeline...")
        
        # Get configuration stats
        gemini_stats = self.gemini_manager.get_api_usage_stats()
        data_stats = self.data_manager.get_data_stats()
        
        print(f"📊 Configuration:")
        print(f"   • Total API keys: {gemini_stats['total_keys']}")
        print(f"   • Stocks in list: {data_stats['total_stocks']}")
        print(f"   • Documents per stock: {max_docs_per_stock}")
        print(f"   • Batch size: {batch_size}")
        print("=" * 50)
        
        # Get stock list
        stock_list = self.data_manager.get_stock_list()
        if stock_list is None or len(stock_list) == 0:
            print("❌ No stocks found in stock list")
            return None
        
        # Step 1: Scrape transcript links in batches
        print(f"\n📋 STEP 1: Scraping transcript links for {len(stock_list)} stocks...")
        temp_files = []
        
        # Progress bar for batches
        total_batches = (len(stock_list) + batch_size - 1) // batch_size
        pbar_batches = tqdm(range(0, len(stock_list), batch_size),
                            desc="📦 Processing batches", unit="batch", total=total_batches)
        
        for batch_start in pbar_batches:
            batch_stocks = stock_list[batch_start: batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            pbar_batches.set_description(f"📦 Processing batch {batch_num}/{total_batches}")
            
            # Use screener extractor to fetch transcripts
            all_transcript_data = self.screener_extractor.batch_fetch_transcripts(
                batch_stocks, max_docs_per_stock
            )
            
            if not all_transcript_data:
                print(f"❌ No transcript links found in batch {batch_num}")
                continue
            
            # Step 2: Extract keywords
            print(f"\n📊 STEP 2: Analyzing keywords for batch {batch_num}...")
            keyword_df = self.analyze_transcript_urls(all_transcript_data)
            if keyword_df.empty:
                print(f"❌ No keywords extracted in batch {batch_num}")
                continue
            
            # Step 3: Generate summaries
            print(f"\n🤖 STEP 3: Generating summaries for batch {batch_num}...")
            summaries_df = self.generate_summaries(keyword_df)
            if summaries_df.empty:
                print(f"❌ No summaries generated in batch {batch_num}")
                continue
            
            # Save batch results
            temp_file = f"{Config.TEMP_FILE_PREFIX}{batch_num}.csv"
            if self.data_manager.save_summaries(summaries_df.to_dict('records'), temp_file):
                temp_files.append(temp_file)
                print(f"💾 Saved batch {batch_num} results to {temp_file}")
        
        pbar_batches.close()
        
        # Step 4: Combine all batch files
        if temp_files:
            print(f"\n📊 STEP 4: Combining {len(temp_files)} batch files...")
            final_df = self.data_manager.combine_batch_files(temp_files)
            
            # Clean up temporary files unless user wants to keep them
            if not save_intermediates:
                self.data_manager.cleanup_temp_files(temp_files)
            else:
                print(f"💾 Intermediate files preserved: {', '.join(temp_files)}")
            
            return final_df
        else:
            print("❌ No batch files were created successfully")
            return None
    
    def get_pipeline_status(self):
        """Get current pipeline status and statistics"""
        return {
            "data_manager": self.data_manager.get_data_stats(),
            "gemini_manager": self.gemini_manager.get_api_usage_stats(),
            "screener_extractor": self.screener_extractor.get_extractor_stats(),
            "keywords_count": len(self.keywords_manager.get_keywords())
        }


def main():
    """Main function to run the pipeline"""
    print("=" * 60)
    print("🏢 AI-POWERED CONCALL SUMMARIZER")
    print("=" * 60)
    
    # Configuration - Load from config file
    print("\n📋 LOADING CONFIGURATION")
    print("-" * 30)
    Config.print_config()
    
    # Validate configuration
    config_issues = Config.validate_config()
    if config_issues:
        print(f"\n❌ Configuration issues found:")
        for issue in config_issues:
            print(f"   • {issue}")
        print("Please fix the configuration in config.py and try again.")
        return
    
    try:
        # Get user input
        print("\n⚙️  CONFIGURATION")
        print("-" * 30)
        
        user_input = input(f"📄 Number of recent documents per stock (default={Config.DEFAULT_DOCS_PER_STOCK}): ")
        max_docs = int(user_input.strip()) if user_input.strip().isdigit() else Config.DEFAULT_DOCS_PER_STOCK
        
        save_intermediates = input("💾 Save intermediate files? (y/n, default=n): ").lower().startswith('y')
        
        batch_input = input(f"📦 Batch size for processing (default={Config.DEFAULT_BATCH_SIZE}): ")
        batch_size = int(batch_input.strip()) if batch_input.strip().isdigit() else Config.DEFAULT_BATCH_SIZE
        
        print(f"\n✅ Configuration set:")
        print(f"   • Documents per stock: {max_docs}")
        print(f"   • Save intermediates: {save_intermediates}")
        print(f"   • Batch size: {batch_size}")
        
        # Initialize and run pipeline
        print(f"\n🔧 INITIALIZING PIPELINE")
        print("-" * 30)
        
        pipeline = StockAnalysisPipeline()
        
        # Show pipeline status
        status = pipeline.get_pipeline_status()
        print(f"\n📊 PIPELINE STATUS")
        print("-" * 30)
        print(f"   • Stocks loaded: {status['data_manager']['total_stocks']}")
        print(f"   • Keywords available: {status['keywords_count']}")
        print(f"   • API keys configured: {status['gemini_manager']['total_keys']}")
        
        # Test Gemini connection
        print(f"\n🔐 TESTING API CONNECTION")
        print("-" * 30)
        if pipeline.gemini_manager.test_api_connection():
            print("✅ Gemini API connection successful")
        else:
            print("❌ Gemini API connection failed - check your API keys")
            return
        
        # Run the pipeline
        print(f"\n🚀 STARTING ANALYSIS")
        print("=" * 60)
        
        start_time = time.time()
        results = pipeline.run_pipeline(
            max_docs_per_stock=max_docs, 
            save_intermediates=save_intermediates,
            batch_size=batch_size
        )
        end_time = time.time()
        
        # Show results
        if results is not None and len(results) > 0:
            print(f"\n📈 PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"   • Execution time: {end_time - start_time:.2f} seconds")
            print(f"   • Stocks processed: {len(results)}")
            print(f"   • Documents per stock: {max_docs}")
            print(f"   • Final output: Pipeline_Final_Summaries.csv")
            
            # Show sample results
            print(f"\n📄 SAMPLE RESULTS (First 3):")
            print("-" * 60)
            for i, (_, row) in enumerate(results.head(3).iterrows()):
                print(f"   {i + 1}. {row['Stock']}: {row['Summary'][:100]}...")
            
            print(f"\n✅ Analysis complete! Check 'Pipeline_Final_Summaries.csv' for full results.")
        else:
            print(f"\n❌ PIPELINE FAILED")
            print("=" * 60)
            print("   • No results were generated")
            print("   • Check the logs above for errors")
    
    except KeyboardInterrupt:
        print(f"\n⏹️  PIPELINE INTERRUPTED")
        print("=" * 60)
        print("   • Analysis stopped by user")
    
    except Exception as e:
        print(f"\n💥 PIPELINE ERROR")
        print("=" * 60)
        print(f"   • Error: {e}")
        print("   • Check your configuration and try again")


if __name__ == "__main__":
    main()
