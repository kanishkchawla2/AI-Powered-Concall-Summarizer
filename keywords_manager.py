# Keywords Manager
# Handles keyword definitions and extraction logic

from config import Config


class KeywordsManager:
    def __init__(self):
        """Initialize with comprehensive keyword sets"""
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

            # Banking & Lending
            "retail banking", "corporate banking", "commercial banking", "wholesale banking", "private banking", "priority banking",
            "lending", "credit growth", "loan book", "loan growth", "loan disbursement", "retail loans", "corporate loans", "personal loans", 
            "home loans", "auto loans", "gold loans", "SME loans", "MSME loans", "agri loans", "working capital loans", 
            "NIM", "net interest margin", "spread", "yields", "deposit rates", "CASA", "current account", "savings account", "time deposits",
            "credit demand", "advances", "loan-to-deposit ratio", "credit cost", "slippages", "restructuring", "provisioning", "write-offs",

            # Insurance
            "life insurance", "general insurance", "health insurance", "motor insurance", "crop insurance", 
            "premiums", "gross written premium", "new business premium", "renewals", "first year premium", 
            "claims ratio", "loss ratio", "combined ratio", "reinsurance", "policyholder surplus", "underwriting", 
            "solvency ratio", "persistency ratio", "embedded value", "value of new business", "protection mix",

            # Capital Markets
            "investment banking", "equity capital markets", "debt capital markets", "M&A advisory", 
            "IPO", "FPO", "QIP", "buyback", "follow-on offering", 
            "brokerage", "trading volumes", "clearing", "settlement", "custody services", 
            "asset management", "mutual funds", "ETF", "AUM", "portfolio management services", "wealth management",

            # Risk & Regulation
            "credit risk", "market risk", "liquidity risk", "operational risk", 
            "capital adequacy ratio", "CRAR", "CET1", "Tier 1 capital", "Tier 2 capital", 
            "risk weighted assets", "stress testing", "Basel norms", "Basel III", 
            "NPA", "GNPA", "NNPA", "provision coverage ratio", "IFRS 9", "Ind AS", "SOX compliance",

            # Payments & Fintech
            "digital payments", "UPI", "NEFT", "RTGS", "IMPS", "mobile wallets", "credit cards", "debit cards", 
            "BNPL", "buy now pay later", "payment gateway", "POS terminals", 
            "neobanks", "digital lending", "fintech partnerships", "API banking", "open banking", "CBDC", "blockchain in BFSI",

            # Macroeconomic & BFSI Drivers
            "interest rates", "monetary policy", "repo rate", "reverse repo", "SLR", "CRR", 
            "liquidity", "credit cycle", "GDP growth", "inflation", "employment", "fiscal deficit", 
            "sovereign bonds", "yield curve", "foreign exchange", "rupee depreciation", "FII flows", "FDI inflows",

           
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
