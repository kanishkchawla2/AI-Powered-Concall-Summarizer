# Data Manager
# Handles Excel operations, stock list management, and data processing

import pandas as pd
import os
from tqdm import tqdm
from config import Config


class DataManager:
    def __init__(self, stock_list_file=None):
        """Initialize data manager with stock list file"""
        self.stock_list_file = stock_list_file or Config.STOCK_LIST_FILE
        self.stock_df = None
        self.stock_list = None
        self.load_stocks()
    
    def load_stocks(self):
        """Load stocks from Excel file"""
        try:
            if os.path.exists(self.stock_list_file):
                self.stock_df = pd.read_excel(self.stock_list_file)
                self.stock_list = self.stock_df["Stock"].dropna().str.lower().unique()
                print(f"✅ Loaded {len(self.stock_list)} stocks from {self.stock_list_file}")
            else:
                print(f"❌ Stock list file {self.stock_list_file} not found")
                self.create_default_stock_list()
        except Exception as e:
            print(f"❌ Error loading stocks: {e}")
            self.create_default_stock_list()
    
    def create_default_stock_list(self):
        """Create a default stock list with popular Indian stocks"""
        default_stocks = [
            'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR', 
            'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'ASIANPAINT',
            'HCLTECH', 'AXISBANK', 'MARUTI', 'SUNPHARMA', 'TITAN', 'ULTRACEMCO',
            'NESTLEIND', 'BAJFINANCE', 'WIPRO', 'TECHM', 'POWERGRID', 'NTPC',
            'DIVISLAB', 'TATAMOTORS', 'ADANIPORTS', 'COALINDIA', 'GRASIM', 'JSWSTEEL',
            'TATACONSUM', 'BAJAJFINSV', 'DRREDDY', 'EICHERMOT', 'APOLLOHOSP', 'BRITANNIA',
            'PIDILITIND', 'SBILIFE', 'HDFCLIFE', 'TATASTEEL', 'BPCL', 'SHREECEM',
            'UPL', 'HINDALCO', 'CIPLA', 'INDUSINDBK', 'HEROMOTOCO', 'ADANIENT', 'ONGC', 'GODREJCP'
        ]
        
        self.stock_df = pd.DataFrame({'Stock': default_stocks})
        self.stock_df.to_excel(self.stock_list_file, index=False)
        self.stock_list = [stock.lower() for stock in default_stocks]
        print(f"✅ Created default stock list with {len(default_stocks)} stocks")
    
    def get_stock_list(self):
        """Get the current stock list"""
        return self.stock_list
    
    def add_stock(self, stock_symbol):
        """Add a new stock to the list"""
        stock_symbol = stock_symbol.upper()
        
        if stock_symbol.lower() not in self.stock_list:
            # Add to dataframe
            new_row = pd.DataFrame({'Stock': [stock_symbol]})
            self.stock_df = pd.concat([self.stock_df, new_row], ignore_index=True)
            
            # Update stock list
            self.stock_list = self.stock_df["Stock"].dropna().str.lower().unique()
            
            # Save to file
            self.stock_df.to_excel(self.stock_list_file, index=False)
            print(f"✅ Added {stock_symbol} to stock list")
        else:
            print(f"⚠️ {stock_symbol} already exists in stock list")
    
    def remove_stock(self, stock_symbol):
        """Remove a stock from the list"""
        stock_symbol = stock_symbol.upper()
        
        if stock_symbol.lower() in self.stock_list:
            # Remove from dataframe
            self.stock_df = self.stock_df[self.stock_df['Stock'].str.upper() != stock_symbol]
            
            # Update stock list
            self.stock_list = self.stock_df["Stock"].dropna().str.lower().unique()
            
            # Save to file
            self.stock_df.to_excel(self.stock_list_file, index=False)
            print(f"✅ Removed {stock_symbol} from stock list")
        else:
            print(f"⚠️ {stock_symbol} not found in stock list")
    
    def create_keyword_dataframe(self, transcript_data, keywords):
        """Create a structured dataframe from transcript data and keywords"""
        all_keyword_data = []
        
        pbar_stocks = tqdm(transcript_data, desc="📊 Processing transcript data", unit="stock")
        
        for stock_group in pbar_stocks:
            if not stock_group:
                continue
                
            stock_name = stock_group[0]['Stock']
            pbar_stocks.set_description(f"📊 Processing {stock_name}")
            
            file_cols = [f"File {i + 1}" for i in range(len(stock_group))]
            summary_table = pd.DataFrame(index=keywords, columns=file_cols).fillna("")
            
            # Add stock name and reset index
            summary_table = summary_table.fillna("-")
            summary_table = summary_table.reset_index()
            summary_table["Stock"] = stock_name
            all_keyword_data.append(summary_table)
        
        pbar_stocks.close()
        return pd.concat(all_keyword_data, ignore_index=True) if all_keyword_data else pd.DataFrame()
    
    def save_summaries(self, summaries_data, filename=None):
        """Save summaries to CSV file"""
        if filename is None:
            filename = Config.FINAL_OUTPUT_FILE
        
        # Create directory if filename contains a path
        if "/" in filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        try:
            df = pd.DataFrame(summaries_data)
            df.to_csv(filename, index=False)
            print(f"💾 Saved summaries to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving summaries: {e}")
            return False
    
    def combine_batch_files(self, temp_files, final_filename=None):
        """Combine multiple batch files into one final file"""
        if final_filename is None:
            final_filename = Config.FINAL_OUTPUT_FILE
            
        if not temp_files:
            print("⚠️ No batch files to combine")
            return None
        
        print(f"\n📊 Combining {len(temp_files)} batch files...")
        pbar_combine = tqdm(temp_files, desc="📊 Reading batch files", unit="file")
        
        combined_dfs = []
        for temp_file in pbar_combine:
            pbar_combine.set_description(f"📊 Reading {temp_file}")
            try:
                df = pd.read_csv(temp_file)
                combined_dfs.append(df)
            except Exception as e:
                print(f"⚠️ Error reading {temp_file}: {e}")
        
        pbar_combine.close()
        
        if combined_dfs:
            combined_df = pd.concat(combined_dfs, ignore_index=True)
            combined_df.to_csv(final_filename, index=False)
            print(f"✅ Combined all batches into {final_filename}")
            return combined_df
        else:
            print("❌ No valid batch files found")
            return None
    
    def cleanup_temp_files(self, temp_files):
        """Clean up temporary files"""
        if not temp_files:
            return
        
        pbar_cleanup = tqdm(temp_files, desc="🧹 Cleaning temp files", unit="file")
        for temp_file in pbar_cleanup:
            pbar_cleanup.set_description(f"🧹 Deleting {temp_file}")
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"⚠️ Error deleting {temp_file}: {e}")
        pbar_cleanup.close()
        
        # Remove temp folder if empty
        try:
            if os.path.exists(Config.TEMP_FOLDER) and not os.listdir(Config.TEMP_FOLDER):
                os.rmdir(Config.TEMP_FOLDER)
        except:
            pass  # Silently ignore if can't remove folder
            
        print("🧹 Temporary files cleaned up")
    
    def get_data_stats(self):
        """Get data statistics"""
        return {
            "stock_list_file": self.stock_list_file,
            "total_stocks": len(self.stock_list) if self.stock_list is not None else 0,
            "stock_list_exists": os.path.exists(self.stock_list_file)
        }
    
    def export_stock_list(self, filename=None):
        """Export current stock list to a new file"""
        if filename is None:
            filename = f"stock_list_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            self.stock_df.to_excel(filename, index=False)
            print(f"✅ Stock list exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting stock list: {e}")
            return False
