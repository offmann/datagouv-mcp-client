"""OpenAI / LLM tool schemas for function calling."""

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_datasets",
            "description": "Search datasets on data.gouv.fr by keywords. Use short, specific queries (API uses AND logic).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"},
                    "page": {"type": "integer", "description": "Page number", "default": 1},
                    "page_size": {"type": "integer", "description": "Results per page", "default": 20},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_info",
            "description": "Get dataset metadata: title, description, organization, resources.",
            "parameters": {
                "type": "object",
                "properties": {"dataset_id": {"type": "string", "description": "Dataset ID"}},
                "required": ["dataset_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dataset_resources",
            "description": "List all resources (files) in a dataset.",
            "parameters": {
                "type": "object",
                "properties": {"dataset_id": {"type": "string", "description": "Dataset ID"}},
                "required": ["dataset_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_resource_info",
            "description": "Get resource metadata: format, size, download URL.",
            "parameters": {
                "type": "object",
                "properties": {"resource_id": {"type": "string", "description": "Resource ID (UUID)"}},
                "required": ["resource_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "download_resource",
            "description": "Download and parse a resource (CSV, JSON, JSONL, Parquet). Use max_rows to limit size.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_id": {"type": "string", "description": "Resource ID"},
                    "max_rows": {"type": "integer", "description": "Max rows to parse (default 100)"},
                    "max_size_mb": {"type": "integer", "description": "Max file size in MB", "default": 500},
                },
                "required": ["resource_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_dataservices",
            "description": "Search dataservices (API catalog) on data.gouv.fr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 20},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataservice_info",
            "description": "Get dataservice metadata.",
            "parameters": {
                "type": "object",
                "properties": {"dataservice_id": {"type": "string", "description": "Dataservice ID"}},
                "required": ["dataservice_id"],
            },
        },
    },
]

OPENAI_TOOLS_OLL = [
    {
        "type": "function",
        "function": {
            "name": "get_rent_stats",
            "description": "Get OLL rent stats (median, quartiles) for agglomeration and housing type. Types: 1P, 2P, 3P, 4P+.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agglomeration": {"type": "string", "description": "City or agglomeration (e.g. Paris, Lyon)"},
                    "type_logement": {"type": "string", "description": "1P, 2P, 3P, or 4P+"},
                },
                "required": ["agglomeration", "type_logement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_rent",
            "description": "Check if a proposed rent is within typical range (OLL data).",
            "parameters": {
                "type": "object",
                "properties": {
                    "agglomeration": {"type": "string"},
                    "type_logement": {"type": "string"},
                    "prix_propose": {"type": "number", "description": "Proposed rent in euros/month"},
                },
                "required": ["agglomeration", "type_logement", "prix_propose"],
            },
        },
    },
]
