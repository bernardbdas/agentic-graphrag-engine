"""Cypher schema definitions, index constraints, and knowledge ontology."""

GRAPH_CONSTRAINTS = [
    # Ensure uniqueness of Company tickers
    "CREATE CONSTRAINT company_ticker_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.ticker IS UNIQUE;",
    # Ensure uniqueness of Subsidiaries
    "CREATE CONSTRAINT subsidiary_id_unique IF NOT EXISTS FOR (s:Subsidiary) REQUIRE s.id IS UNIQUE;",
    # Ensure uniqueness of Risk Factors
    "CREATE CONSTRAINT risk_id_unique IF NOT EXISTS FOR (r:RiskFactor) REQUIRE r.id IS UNIQUE;",
    # Full-text index for fuzzy company entity search
    "CREATE FULLTEXT INDEX company_fulltext_idx IF NOT EXISTS FOR (c:Company) ON EACH [c.name, c.ticker, c.sector];",
]

SAMPLE_FINANCIAL_TRIPLES = [
    # Apple ecosystem
    {
        "head": "AAPL",
        "head_label": "Company",
        "head_name": "Apple Inc.",
        "rel": "SUPPLIED_BY",
        "tail": "TSM",
        "tail_label": "Company",
        "tail_name": "Taiwan Semiconductor Manufacturing Co.",
        "weight": 0.95,
    },
    {
        "head": "AAPL",
        "head_label": "Company",
        "head_name": "Apple Inc.",
        "rel": "SUPPLIED_BY",
        "tail": "CRUS",
        "tail_label": "Company",
        "tail_name": "Cirrus Logic Inc.",
        "weight": 0.88,
    },
    {
        "head": "AAPL",
        "head_label": "Company",
        "head_name": "Apple Inc.",
        "rel": "COMPETES_WITH",
        "tail": "MSFT",
        "tail_label": "Company",
        "tail_name": "Microsoft Corp.",
        "weight": 0.90,
    },
    {
        "head": "AAPL",
        "head_label": "Company",
        "head_name": "Apple Inc.",
        "rel": "EXPOSED_TO_RISK",
        "tail": "RISK_GEOPOLITICAL_TAIWAN",
        "tail_label": "RiskFactor",
        "tail_name": "Taiwan Strait Geopolitical Supply Disruption",
        "weight": 0.85,
    },
    # Nvidia ecosystem
    {
        "head": "NVDA",
        "head_label": "Company",
        "head_name": "NVIDIA Corporation",
        "rel": "SUPPLIED_BY",
        "tail": "TSM",
        "tail_label": "Company",
        "tail_name": "Taiwan Semiconductor Manufacturing Co.",
        "weight": 0.99,
    },
    {
        "head": "NVDA",
        "head_label": "Company",
        "head_name": "NVIDIA Corporation",
        "rel": "SUPPLIES_CHIPS_TO",
        "tail": "MSFT",
        "tail_label": "Company",
        "tail_name": "Microsoft Corp.",
        "weight": 0.92,
    },
    {
        "head": "NVDA",
        "head_label": "Company",
        "head_name": "NVIDIA Corporation",
        "rel": "SUPPLIES_CHIPS_TO",
        "tail": "META",
        "tail_label": "Company",
        "tail_name": "Meta Platforms Inc.",
        "weight": 0.89,
    },
    {
        "head": "NVDA",
        "head_label": "Company",
        "head_name": "NVIDIA Corporation",
        "rel": "EXPOSED_TO_RISK",
        "tail": "RISK_EXPORT_RESTRICTIONS",
        "tail_label": "RiskFactor",
        "tail_name": "US Advanced Compute Export Restrictions",
        "weight": 0.91,
    },
    # Microsoft ecosystem
    {
        "head": "MSFT",
        "head_label": "Company",
        "head_name": "Microsoft Corp.",
        "rel": "INVESTED_IN",
        "tail": "OPENAI",
        "tail_label": "Company",
        "tail_name": "OpenAI Inc.",
        "weight": 0.95,
    },
    {
        "head": "MSFT",
        "head_label": "Company",
        "head_name": "Microsoft Corp.",
        "rel": "COMPETES_WITH",
        "tail": "GOOGL",
        "tail_label": "Company",
        "tail_name": "Alphabet Inc.",
        "weight": 0.94,
    },
]
