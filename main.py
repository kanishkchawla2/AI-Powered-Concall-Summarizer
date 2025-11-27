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
    
    def run_pipeline(self, max_docs_per_stock=None, save_intermediates=False, batch_size=None, check_existing=False, stock_subset=None):
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
        print(f"   • Resume from temp files: {check_existing}")
        print("=" * 50)
        
        # Get stock list
        stock_list = self.data_manager.get_stock_list()
        if stock_list is None or len(stock_list) == 0:
            print("❌ No stocks found in stock list")
            return None

        # If a subset is provided, intersect with available stocks (case-insensitive)
        if stock_subset is not None:
            try:
                # Normalize to lowercase for comparison
                base_set = set([str(s).strip().lower() for s in stock_list if str(s).strip()])
                desired = [str(s).strip().lower() for s in stock_subset if str(s).strip()]
                filtered = [s for s in desired if s in base_set]
                print(f"🔎 Applying subset filter: requested={len(desired)}, matched={len(filtered)}")
                if not filtered:
                    print("⚠️ None of the requested stocks were found in the main stock list. Aborting.")
                    return None
                stock_list = filtered
            except Exception as e:
                print(f"⚠️ Error applying stock subset: {e}")
                return None
        
        # Debug info
        print(f"📊 Stock list type: {type(stock_list)}")
        if hasattr(stock_list, 'shape'):
            print(f"📊 Stock list shape: {stock_list.shape}")
        print(f"📊 Stock list length: {len(stock_list)}")
        
        # Check for existing progress and filter if requested
        if check_existing:
            print(f"\n🔍 CHECKING TEMP FILES FOR PROGRESS")
            print("-" * 30)
            try:
                existing_stocks = self.check_existing_summaries()
                stock_list = self.filter_stocks_to_process(stock_list, existing_stocks)
                
                if not stock_list:
                    print("✅ All stocks already processed in temp files! No new processing needed.")
                    return None
            except Exception as e:
                print(f"⚠️ Error checking existing progress: {e}")
                print("Continuing with all stocks...")
                # Continue with original stock list if there's an error
        
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
            # Ensure the temp directory exists
            os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
            if self.data_manager.save_summaries(summaries_df.to_dict('records'), temp_file):
                temp_files.append(temp_file)
                print(f"💾 Saved batch {batch_num} results to {temp_file}")
        
        pbar_batches.close()
        
        # Step 4: Combine all batch files (including existing ones if checking progress)
        all_temp_files = temp_files.copy()
        
        # If checking existing, also include previously created batch files
        if check_existing:
            temp_folder = Config.TEMP_FOLDER
            if os.path.exists(temp_folder):
                existing_batch_files = []
                # Get just the filename part of the prefix for comparison
                prefix_filename = os.path.basename(Config.TEMP_FILE_PREFIX)
                for file in os.listdir(temp_folder):
                    if file.startswith(prefix_filename) and file.endswith('.csv'):
                        full_path = os.path.join(temp_folder, file)
                        if full_path not in temp_files:  # Don't duplicate newly created files
                            existing_batch_files.append(full_path)
                
                if existing_batch_files:
                    print(f"� Including {len(existing_batch_files)} existing batch files")
                    all_temp_files.extend(existing_batch_files)
        
        if all_temp_files:
            print(f"\n📊 STEP 4: Combining {len(all_temp_files)} batch files...")
            final_df = self.data_manager.combine_batch_files(all_temp_files)
            
            # Clean up temporary files unless user wants to keep them
            # Only clean up newly created files, not existing ones when check_existing=True
            files_to_cleanup = temp_files if check_existing else all_temp_files
            
            if not save_intermediates and files_to_cleanup:
                self.data_manager.cleanup_temp_files(files_to_cleanup)
                if check_existing and temp_files:
                    print(f"💾 Cleaned up {len(temp_files)} new batch files, preserved existing ones")
            else:
                print(f"💾 All batch files preserved: {len(all_temp_files)} total files")
            
            return final_df
        else:
            print("❌ No batch files were created successfully")
            return None
    
    def check_existing_summaries(self, temp_folder=None):
        """Check for existing summaries in temporary batch files"""
        existing_stocks = []
        try:
            # Use config temp folder if not provided
            if temp_folder is None:
                temp_folder = Config.TEMP_FOLDER
            
            # Check if temp folder exists
            if not os.path.exists(temp_folder):
                print("📄 No temp folder found - will process all stocks")
                return []
            
            # Find all batch files in temp folder
            batch_files = []
            # Get just the filename part of the prefix for comparison
            prefix_filename = os.path.basename(Config.TEMP_FILE_PREFIX)
            for file in os.listdir(temp_folder):
                if file.startswith(prefix_filename) and file.endswith('.csv'):
                    batch_files.append(os.path.join(temp_folder, file))
            
            if not batch_files:
                print("📄 No existing batch files found - will process all stocks")
                return []
            
            print(f"📋 Found {len(batch_files)} existing batch files:")
            
            # Read all batch files and collect processed stocks
            for batch_file in sorted(batch_files):
                try:
                    batch_df = pd.read_csv(batch_file)
                    if 'Stock' in batch_df.columns:
                        batch_stocks = batch_df['Stock'].unique().tolist()
                        existing_stocks.extend(batch_stocks)
                        print(f"   • {os.path.basename(batch_file)}: {len(batch_stocks)} stocks")
                    else:
                        print(f"   ⚠️ {os.path.basename(batch_file)}: No 'Stock' column found")
                except Exception as e:
                    print(f"   ⚠️ Error reading {os.path.basename(batch_file)}: {e}")
            
            # Remove duplicates
            existing_stocks = list(set(existing_stocks))
            
            if existing_stocks:
                print(f"📊 Total unique stocks already processed: {len(existing_stocks)}")
                print("📝 Processed stocks:")
                for i, stock in enumerate(existing_stocks[:10]):  # Show first 10
                    print(f"   • {stock}")
                if len(existing_stocks) > 10:
                    print(f"   ... and {len(existing_stocks) - 10} more")
            
            return existing_stocks
            
        except Exception as e:
            print(f"⚠️ Error checking temp folder: {e}")
            return []
    
    def filter_stocks_to_process(self, stock_list, existing_stocks):
        """Filter out stocks that already have summaries (case-insensitive)"""
        if not existing_stocks:
            print("🟢 No existing processed stocks detected. Processing full list.")
            return stock_list

        # Normalize both lists to lowercase strings (strip whitespace)
        def _norm_list(seq):
            out = []
            if hasattr(seq, 'tolist'):
                try:
                    seq = seq.tolist()
                except:
                    pass
            for x in seq:
                if x is None:
                    continue
                x = str(x).strip()
                if not x:
                    continue
                out.append(x.lower())
            return out

        normalized_stock_list = _norm_list(stock_list)
        normalized_existing = set(_norm_list(existing_stocks))

        # Build mapping from normalized -> original (first occurrence) so we can return originals
        original_map = {}
        # Ensure stock_list iterable
        if hasattr(stock_list, 'tolist'):
            stock_list_iter = stock_list.tolist()
        else:
            stock_list_iter = list(stock_list)
        for orig in stock_list_iter:
            key = str(orig).strip().lower()
            if key and key not in original_map:
                original_map[key] = orig

        # Filter out those present in existing
        filtered_keys = [k for k in normalized_stock_list if k not in normalized_existing]
        stocks_to_process = [original_map[k] for k in filtered_keys]
        skipped_count = len(stock_list_iter) - len(stocks_to_process)

        print("📊 Stock filtering results:")
        print(f"   • Total stocks (raw): {len(stock_list_iter)}")
        print(f"   • Already processed (matched case-insensitive): {skipped_count}")
        print(f"   • Remaining to process: {len(stocks_to_process)}")

        if skipped_count:
            # Show sample skipped
            skipped_keys = [k for k in normalized_stock_list if k in normalized_existing][:10]
            if skipped_keys:
                print("   • Sample skipped:")
                for k in skipped_keys:
                    print(f"     - {original_map.get(k, k)}")

        if stocks_to_process:
            print("📝 Sample to process:")
            for s in stocks_to_process[:10]:
                print(f"   • {s}")
            if len(stocks_to_process) > 10:
                print(f"   ... and {len(stocks_to_process) - 10} more")
        else:
            print("✅ All stocks already processed.")

        return stocks_to_process

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
        
        # Ask about checking existing summaries
        print("📋 PROCESSING MODE:")
        print("   1. Resume from temp files - skip already processed stocks")
        print("   2. Start fresh - process all stocks (ignore temp files)")
        
        mode_choice = input("Choose processing mode (1/2, default=1): ").strip()
        check_existing = mode_choice != "2"

        # Ask whether to process all stocks or a subset from an Excel file
        print("\n📋 STOCK SELECTION MODE:")
        print("   A. All stocks from main list")
        print("   B. Only stocks listed in an Excel file (must have a 'Stock' column)")
        stock_mode = input("Choose stock selection (A/B, default=A): ").strip().upper()
        subset_file = None
        subset_list = None
        if stock_mode == "B":
            subset_file = input("📄 Enter path to Excel file with a 'Stock' column: ").strip()
            try:
                tmp_df = pd.read_excel(subset_file)
                if 'Stock' not in tmp_df.columns:
                    print("❌ Excel file must contain a 'Stock' column. Aborting.")
                    return
                subset_list = tmp_df['Stock'].dropna().tolist()
                print(f"🔎 Loaded {len(subset_list)} stocks from {subset_file}")
            except Exception as e:
                print(f"❌ Failed to read subset file: {e}")
                return
        
        user_input = input(f"📄 Number of recent documents per stock (default={Config.DEFAULT_DOCS_PER_STOCK}): ")
        max_docs = int(user_input.strip()) if user_input.strip().isdigit() else Config.DEFAULT_DOCS_PER_STOCK
        
        save_intermediates = input("💾 Save intermediate files? (y/n, default=n): ").lower().startswith('y')
        
        batch_input = input(f"📦 Batch size for processing (default={Config.DEFAULT_BATCH_SIZE}): ")
        batch_size = int(batch_input.strip()) if batch_input.strip().isdigit() else Config.DEFAULT_BATCH_SIZE
        
        print(f"\n✅ Configuration set:")
        print(f"   • Processing mode: {'Resume from temp files' if check_existing else 'Start fresh'}")
        if subset_list is not None:
            print(f"   • Stock selection: Subset from file ({len(subset_list)} stocks)")
        else:
            print(f"   • Stock selection: All stocks")
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
            batch_size=batch_size,
            check_existing=check_existing,
            stock_subset=subset_list
        )
        end_time = time.time()
        
        duration_min = (end_time - start_time) / 60
        print(f"\n✅ Analysis complete! Duration: {duration_min:.1f} minutes")
        
        if results is not None and not results.empty:
            # Display final summary statistics
            print(f"\n📊 FINAL SUMMARY STATISTICS")
            print("-" * 30)
            print(f"   • Total stocks processed: {results['Stock'].nunique()}")
            print(f"   • Total summaries generated: {len(results)}")
            print(f"   • Total keywords matched: {results.filter(like='File').count().sum()}")
            
            # Show sample results
            sample_size = min(5, len(results))
            print(f"\n📋 SAMPLE RESULTS ({sample_size} entries)")
            print(results.sample(sample_size, random_state=42).to_string(index=False))
            
            # Save final results to CSV
            output_file = Config.OUTPUT_FILE
            results.to_csv(output_file, index=False)
            print(f"💾 Final results saved to: {output_file}")
        else:
            print("❌ No results to display")
    
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return

    print("=" * 60)
    print("Thank you for using the AI-Powered Concall Summarizer!")
    print("For best results, review and adjust the configuration in config.py")
    print("=" * 60)


# This line ensures that the main() function will be called when the script is run directly.
if __name__ == "__main__":
    main()
