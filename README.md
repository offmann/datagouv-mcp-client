# datagouv-mcp-client

Python client for [data.gouv.fr](https://www.data.gouv.fr) – MCP-compatible tools for datasets, resources, and open data. Use it in LLM agents, scripts, or as a library.

## Features

- **Search datasets** – Find datasets by keywords
- **Dataset & resource metadata** – Get info, list resources
- **Download & parse** – Fetch CSV, JSON, JSONL, Parquet (no local cache; data stays on data.gouv.fr)
- **Dataservices** – Search and inspect API catalog
- **Extensible** – Register custom tools, plug in OLL (rent) data

## Install

```bash
pip install datagouv-mcp-client
```

Or from source:

```bash
git clone https://github.com/your-username/datagouv-mcp-client.git
cd datagouv-mcp-client
pip install -e .
```

## Quick start

```python
from datagouv_client import DatagouvClient

client = DatagouvClient()

# Search datasets
result = client.search_datasets("loyers")
print(result["datasets"][:3])

# Get dataset info
info = client.get_dataset_info("56fd8e8788ee387079c352f7")
print(info["title"], info["resources_count"])

# List resources
resources = client.list_dataset_resources("56fd8e8788ee387079c352f7")
for r in resources["resources"][:5]:
    print(r["title"], r["format"])
```

## Use with LLM agents (OpenAI)

```python
from datagouv_client import DatagouvClient, get_openai_tools, run_tool

client = DatagouvClient()
tools = get_openai_tools()

# In your agent loop, when the LLM returns a tool call:
result = run_tool("search_datasets", {"query": "qualité air"}, client)
```

## Extending the client

### Register a custom tool

```python
from datagouv_client import DatagouvClient, register_tool, run_tool

def my_custom_tool(client: DatagouvClient, args: dict) -> dict:
    # Your logic here
    return {"result": "..."}

register_tool("my_custom_tool", my_custom_tool)
```

### Add OLL (rent) tools

OLL tools require loading Observatoires Locaux des Loyers data. See `examples/oll_agent.py` for a full example with rent stats and price checks.

## Data handling

- **No local storage** – Data is fetched from data.gouv.fr on demand
- **Size limits** – `download_resource` supports `max_rows` and `max_size_mb` to avoid large transfers
- **Formats** – CSV, JSON, JSONL, Parquet

## API reference

| Method | Description |
|--------|-------------|
| `search_datasets(query, page, page_size)` | Search datasets by keywords |
| `get_dataset_info(dataset_id)` | Get dataset metadata |
| `list_dataset_resources(dataset_id)` | List resources in a dataset |
| `get_resource_info(resource_id)` | Get resource metadata |
| `download_resource(resource_id, max_rows, max_size_mb)` | Download and parse a resource |
| `search_dataservices(query, page, page_size)` | Search dataservices |
| `get_dataservice_info(dataservice_id)` | Get dataservice metadata |

## Contributing

Contributions are welcome. To add a new tool:

1. **Implement** in `src/datagouv_client/tools/` (e.g. `datasets.py`, `resources.py`)
2. **Expose** in `client.py` as a `DatagouvClient` method
3. **Register** in `client._TOOL_RUNNERS` and `tools/schemas.py` (for LLM use)
4. **Document** in this README

Example:

```python
# In tools/my_tool.py
def my_tool(base_url: str, arg: str, timeout: int = 30) -> dict:
    ...

# In client.py
def my_tool(self, arg: str) -> dict:
    return tools.my_tool(self.base_url, arg, self.timeout)

# Register for run_tool()
register_tool("my_tool", lambda c, a: c.my_tool(a["arg"]))
```

## License

MIT
