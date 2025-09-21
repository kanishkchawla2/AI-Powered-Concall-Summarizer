# AI-Powered Concall Summarizer - Modular Structure

This project has been refactored into a modular architecture for better maintainability and easier feature addition.

## 📁 Project Structure

### Core Modules

1. **`main.py`** - Main orchestrator
   - Coordinates all modules
   - Handles user input and pipeline execution
   - Provides comprehensive status reporting

2. **`config.py`** - Configuration manager
   - Centralized configuration settings
   - API keys management
   - Pipeline parameters
   - Easy to modify settings

3. **`data_manager.py`** - Data operations
   - Excel file handling
   - Stock list management
   - CSV operations and file management
   - Data validation and cleanup

4. **`keywords_manager.py`** - Keywords handling
   - Keyword definitions and categories
   - Context extraction around keywords
   - Keyword filtering and matching
   - Easy to add/remove keywords

5. **`screener_extractor.py`** - Web scraping
   - Screener.in data extraction
   - PDF and webpage text extraction
   - Multiple driver management
   - Retry logic and error handling

6. **`gemini_manager.py`** - AI operations
   - Gemini API integration
   - API key rotation
   - Summary generation
   - Rate limiting and error handling

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Configure API Keys**
   - Edit `config.py`
   - Add your Gemini API keys to `GEMINI_API_KEYS` list

3. **Run the Pipeline**
   ```bash
   python main.py
   ```

## 🔧 Configuration

All settings are centralized in `config.py`:

- **API Keys**: Add your Gemini API keys
- **File Paths**: Configure input/output files
- **Pipeline Settings**: Batch sizes, retry limits
- **Web Scraping**: Driver settings, delays
- **Keywords**: Context window, match limits

## 📊 Features

### Easy Feature Addition

1. **Add New Keywords**
   ```python
   # In keywords_manager.py
   keywords_manager.add_keyword("new_financial_term")
   ```

2. **Modify AI Instructions**
   ```python
   # In config.py
   SYSTEM_INSTRUCTION = "Your custom instruction..."
   ```

3. **Add New Data Sources**
   ```python
   # Create new extractor in screener_extractor.py
   def extract_from_new_source(self, url):
       # Implementation
   ```

4. **Change Stock Lists**
   ```python
   # In data_manager.py
   data_manager.add_stock("NEWSTOCK")
   data_manager.remove_stock("OLDSTOCK")
   ```

### Improved Error Handling

- Individual module error isolation
- Comprehensive logging
- Graceful degradation
- Detailed status reporting

### Better Performance

- Modular processing
- Concurrent operations
- Efficient data management
- Memory optimization

## 🛠 Development Workflow

### Adding New Features

1. **Identify the appropriate module**
   - Data operations → `data_manager.py`
   - Web scraping → `screener_extractor.py`
   - AI/ML → `gemini_manager.py`
   - Keywords → `keywords_manager.py`
   - Configuration → `config.py`

2. **Add your feature**
   ```python
   def new_feature(self, parameters):
       """Your new feature implementation"""
       pass
   ```

3. **Update main.py if needed**
   ```python
   # Add to pipeline execution
   result = self.module.new_feature(params)
   ```

4. **Test the feature**
   ```bash
   python main.py
   ```

### Extending Modules

Each module is designed to be easily extensible:

```python
# Example: Adding a new keyword category
class KeywordsManager:
    def add_category(self, category_name, keywords_list):
        """Add a new keyword category"""
        # Implementation
```

## 📈 Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual modules can be tested separately
3. **Scalability**: Easy to add new features without affecting others
4. **Reusability**: Modules can be reused in other projects
5. **Debugging**: Easier to isolate and fix issues
6. **Collaboration**: Multiple developers can work on different modules

## 🔍 Module Dependencies

```
main.py
├── config.py
├── data_manager.py
├── keywords_manager.py
├── screener_extractor.py
└── gemini_manager.py
```

Each module is designed to be independent with minimal cross-dependencies.

## 📝 Example Usage

```python
# Initialize components
data_manager = DataManager("my_stocks.xlsx")
keywords_manager = KeywordsManager()
screener_extractor = ScreenerExtractor()
gemini_manager = GeminiManager(api_keys)

# Use individually
stocks = data_manager.get_stock_list()
keywords = keywords_manager.get_keywords()
transcripts = screener_extractor.fetch_transcript_links("RELIANCE")
summary = gemini_manager.generate_summary("RELIANCE", keyword_data)
```

## 🚨 Error Handling

Each module includes comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **API errors**: Graceful degradation and key rotation
- **Data errors**: Validation and cleanup
- **File errors**: Backup and recovery mechanisms

## 📊 Monitoring & Logging

- Real-time progress bars
- Detailed status reporting
- Error tracking and reporting
- Performance metrics

This modular structure makes the codebase much more maintainable and allows for easy addition of new features without affecting existing functionality.
