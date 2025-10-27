# 🤖 AI-Powered Concall Summarizer for 1800+ Stocks

### Accelerating qualitative research through automation and intelligent summarization

---

## 📘 Overview

In equity research, analysts spend **hours** manually reading concall transcripts to extract insights about management tone, guidance, and future plans.
This project reimagines that process with **AI automation** — reducing hours of qualitative work into **minutes**.

The **AI-Powered Concall Summarizer** automates the end-to-end analysis pipeline for **1800+ listed Indian companies**.
It scrapes concall transcripts from *Screener.in*, extracts context-rich financial commentary using **75+ domain-specific keywords**, and generates **Gemini AI–powered summaries** highlighting what truly matters — in less than a minute per company.

---

## 🚀 What It Does

### 💡 Core Idea

> Transform unstructured concall transcripts into concise, finance-focused summaries using keyword intelligence and AI reasoning.

### ⚙️ Pipeline in Action

1. **Scraping** – Extracts transcripts (PDF/web) for each company from *Screener.in*
2. **Keyword Filtering** – Detects relevant signals across 75+ financial terms like *margin, capex, guidance, demand, cost pressures,* etc.
3. **AI Summarization** – Sends filtered, context-rich excerpts to **Gemini AI** for final summaries
4. **Excel Integration** – Automatically exports summaries for each company into structured Excel sheets — ready for live analysis and reporting

---

## 📊 Key Outcomes

| Metric                            | Before                  | After                               |
| --------------------------------- | ----------------------- | ----------------------------------- |
| Average analysis time per company | ~30 minutes             | < 1 minute                          |
| Coverage                          | ~50–100 stocks manually | 1800+ automated                     |
| Output format                     | Raw text                | Concise AI summaries + Excel export |

### 🧠 Key Takeaways

* Built a **3-stage automation pipeline** (Scraping → Keyword Filtering → AI Summarization)
* Extracted **high-signal context** from unstructured data across multiple sectors
* Integrated with Excel for **instant visualization and strategic decision-making**
* Designed the system for **scalability and easy integration** with other data sources

---

## 🗂 File Structure

```
main.py
├── config.py
├── data_manager.py
├── keywords_manager.py
├── screener_extractor.py
└── gemini_manager.py
```

### 🧠 Component Overview

| File                        | Responsibility                                                              |
| --------------------------- | --------------------------------------------------------------------------- |
| **`main.py`**               | Central orchestrator that runs the full pipeline                            |
| **`config.py`**             | Configuration hub for API keys, file paths, and parameters                  |
| **`data_manager.py`**       | Manages Excel I/O, CSV handling, and data validation                        |
| **`keywords_manager.py`**   | Stores and manages financial keywords, context windows, and filtering logic |
| **`screener_extractor.py`** | Scrapes Screener.in, extracts text from PDFs/webpages, handles retries      |
| **`gemini_manager.py`**     | Manages Gemini API calls, key rotation, rate limits, and summarization      |

---

## 🛠 Quick Start

### 1️⃣ Setup Environment

```bash
source venv/bin/activate
```

### 2️⃣ Add Gemini API Keys

Edit `config.py`:

```python
GEMINI_API_KEYS = ["your_api_key_1", "your_api_key_2"]
```

### 3️⃣ Run the Pipeline

```bash
python main.py
```

---

## ⚙️ Customization & Extensibility

### Add New Keywords

```python
# In keywords_manager.py
keywords_manager.add_keyword("operating leverage")
```

### Modify AI Prompt

```python
# In config.py
SYSTEM_INSTRUCTION = "Focus more on margin guidance and demand outlook."
```

### Add New Data Source

```python
# In screener_extractor.py
def extract_from_new_source(self, url):
    # Implementation here
```

### Change Stock Universe

```python
data_manager.add_stock("TCS")
data_manager.remove_stock("XYZCORP")
```

---

## ⚡ Performance & Reliability

✅ **Concurrent Execution** – Handles hundreds of transcripts efficiently
✅ **Error Isolation** – Each process fails gracefully without stopping the pipeline
✅ **API Key Rotation** – Automatically switches keys to prevent rate-limit interruptions
✅ **Logging & Status Reports** – Real-time tracking of progress and errors

---

## 🧠 Example Usage

```python
data_manager = DataManager("stocks.xlsx")
keywords_manager = KeywordsManager()
screener_extractor = ScreenerExtractor()
gemini_manager = GeminiManager(api_keys)

stocks = data_manager.get_stock_list()
keywords = keywords_manager.get_keywords()
transcript = screener_extractor.fetch_transcript_links("RELIANCE")
summary = gemini_manager.generate_summary("RELIANCE", keywords)
```

---

## 🧾 Error Handling & Logging

* Automatic **retry** on failed network/API calls
* **Exponential backoff** for rate-limiting
* **Data validation** before summarization
* **Comprehensive logs** for debugging and performance monitoring

---

## 🧭 Vision

The long-term goal is to evolve this project into a **sector-intelligence dashboard**, integrating:

* Real-time financial commentary tracking
* Automated fundamental screening
* Predictive insights from historical management tone

---

## 📎 [Project Link & Demo]

*(Add your GitHub link or demo video here once ready)*
