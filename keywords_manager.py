# Keywords Manager
# Handles keyword definitions and extraction logic

from config import Config


class KeywordsManager:
    def __init__(self):
        """Initialize with comprehensive keyword sets"""
        self.keywords = [
    # Financials
    "revenue","sales","topline","ebitda","ebit","pat","profit","margin","gm","om","nm",
    "realization","realise","pricing","price","spreads","mix","volume","volumes","opex","cost","costs",

    # Inputs & RM
    "rm","raw material","input","commodity","energy","power","electricity","fuel","gas","cotton","chemicals",

    # Capex & Capacity
    "capex","expansion","capacity","utilization","util","commission","commenced","debottleneck","brownfield","greenfield","automation","modernization",

    # Balance Sheet & Cash
    "fcf","free cash","cash flow","working capital","inventory","receivables","payables",
    "net debt","gross debt","debt","leverage","gearing","interest","finance cost","borrowing","coverage",

    # Returns & Ratios
    "roce","roe","asset turnover","return","yield",

    # Demand & Market
    "demand","orders","order book","visibility","market","market share",
    "product mix","premium","premiumization","domestic","exports","export","geo mix","international","channel",

    # Cycles & Seasonality
    "seasonality","seasonal","festive","wedding","monsoon","destock","destocking","restock","restocking",

    # Macro & Policy
    "macro","headwinds","tailwinds","regulatory","regulation","policy","subsidy","incentive",
    "tax","taxation","duties","duty","customs","pli","budget","inflation","rates","interest rate","repo",

    # Management Tone
    "guidance","outlook","commentary","visibility","confidence","cautious","optimistic","strong","muted","softness","weakness","volatility","stability",

    # Supply Chain & Execution
    "supply","supply chain","logistics","freight","shipping","transport","warehousing",
    "sourcing","procurement","constraints","bottleneck","delays","execution",

    # Accounting
    "depreciation","amortization","policy change","accounting","one-off","exceptional","extraordinary","restatement",

    # Corporate Actions
    "promoter","pledge","buyback","dividend","shareholding","equity","capital raise","qip","rights",

    # ESG / Energy
    "sustainability","esg","renewable","solar","wind","ppa","tariff","savings","energy efficiency","mw","carbon","emissions",

    # BFSI (high-density)
    "nim","spread","yield","casa","deposits","advances","loan","loan growth","credit growth",
    "slippages","slippage","npa","gnpa","nnpa","asset quality","provision","provisioning","write-off","credit cost","delinquencies","aum",

    # Insurance
    "gwp","premium","premiums","claims","claim","loss ratio","combined ratio",
    "solvency","persistency","vnb","embedded value","protection mix",

    # Capital Markets
    "ib","ecm","dcm","markets","brokerage","trading","turnover","volumes","etf","pms","wealth","mf","mutual fund","aum",

    # Payments / Fintech
    "upi","bnpl","gateway","pos","digital","api","cbdc","payment","fintech","wallet",

    # Macro BFSI
    "repo","reverse repo","slr","crr","liquidity","inflation","gdp","fii","fdi","fx","currency","rupee"
]

    
    def get_keywords(self):
        """Return the list of keywords"""
        return self.keywords
    
    def add_keyword(self, keyword):
        """Add a new keyword to the list"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            print(f"✅ Added keyword: {keyword}")
        else:
            print(f"⚠️ Keyword '{keyword}' already exists")
    
    def remove_keyword(self, keyword):
        """Remove a keyword from the list"""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            print(f"✅ Removed keyword: {keyword}")
        else:
            print(f"⚠️ Keyword '{keyword}' not found")
    
    def extract_keyword_context(self, text, keyword, context_words=None):
        """Extract context around keywords (N words before and after)"""
        if context_words is None:
            context_words = Config.CONTEXT_WORDS
        
        words = text.split()
        contexts = []
        for i, word in enumerate(words):
            if keyword in word.lower():
                start = max(i - context_words, 0)
                end = min(i + context_words, len(words))
                snippet = " ".join(words[start:end])
                contexts.append(snippet)
        return contexts
    
    def filter_keywords(self, text, max_matches_per_keyword=None):
        """Filter and extract keyword contexts from text"""
        if max_matches_per_keyword is None:
            max_matches_per_keyword = Config.MAX_MATCHES_PER_KEYWORD
            
        filtered = {}
        for kw in self.keywords:
            matches = self.extract_keyword_context(text.lower(), kw)
            if matches:
                print(f"🔍 Found keyword '{kw}' in: {matches[0][:100]}...")
                filtered[kw] = matches[:max_matches_per_keyword]
        return filtered
    
    def get_keywords_by_category(self):
        """Return keywords organized by category for better management"""
        categories = {
            "Financial": [
                "revenue", "topline", "bottomline", "EBITDA", "EBIT", "PAT", "net profit",
                "gross margin", "margins", "operating leverage", "cost pressure", "input cost",
                "realization", "pricing power", "price hike", "discounting"
            ],
            "Costs": [
                "raw material", "RM cost", "energy cost", "power cost", "gas prices",
                "opex", "cost optimization", "efficiency", "productivity", "cost leadership"
            ],
            "Growth": [
                "capex", "expansion", "capacity utilization", "commissioning",
                "greenfield", "brownfield", "debottlenecking", "backward integration"
            ],
            "Balance Sheet": [
                "free cash flow", "working capital", "cash conversion",
                "net debt", "debt reduction", "interest coverage", "leverage", "finance cost",
                "capital adequacy", "collections", "disbursement"
            ],
            "Ratios": [
                "ROCE", "ROE", "asset turnover", "inventory days", "receivable days", "payable days"
            ],
            "Business": [
                "demand", "volume growth", "product mix", "premiumization",
                "channel mix", "SKU", "new launch", "market share",
                "domestic", "exports", "geo mix", "international business"
            ],
            "Seasonality": [
                "festive season", "wedding season", "monsoon",
                "seasonality", "inventory build-up", "destocking", "restocking", "inventory correction"
            ],
            "Macro": [
                "headwinds", "tailwinds", "macro uncertainty", "regulatory environment",
                "GST", "budget impact", "PLI", "FAME", "subsidy", "tax rate", "duty impact", "customs"
            ],
            "Outlook": [
                "guidance", "outlook", "visibility", "confident", "cautious", "optimistic",
                "conservative", "hopeful", "strong growth", "muted", "rebound", "softness",
                "moderation", "volatility", "stability"
            ],
            "Operations": [
                "supply chain", "logistics", "freight cost", "warehousing",
                "sourcing", "import substitution", "supply constraints", "project delays"
            ],
            "Corporate Actions": [
                "promoter holding", "pledge", "buyback", "dividend payout", "shareholding"
            ],
            "Technology & ESG": [
                "AI adoption", "EV transition", "sustainability", "ESG", "carbon footprint",
                "green initiatives", "R&D", "innovation", "automation", "digital transformation",
                "cybersecurity", "cloud adoption", "patents", "benchmarking"
            ],
            "Workforce": [
                "attrition", "hiring", "utilization", "offshore", "onsite",
                "subcontracting", "bench", "billed effort"
            ]
        }
        return categories
