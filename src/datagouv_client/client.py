"""
Client and tool registry – extensible entry point for data.gouv.fr tools.
"""

from typing import Any, Callable

from datagouv_client.tools import datasets, resources


class DatagouvClient:
    """
    Client for data.gouv.fr API. Provides MCP-compatible tools.

    Usage:
        client = DatagouvClient()
        result = client.search_datasets("loyers")
        result = client.get_dataset_info("56fd8e8788ee387079c352f7")
    """

    def __init__(self, base_url: str = "https://www.data.gouv.fr/api/1", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._oll_df: Any = None

    def search_datasets(self, query: str, page: int = 1, page_size: int = 20) -> dict:
        """Search datasets by keywords. Use short, specific queries (API uses AND logic)."""
        return datasets.search_datasets(self.base_url, query, page, page_size, self.timeout)

    def get_dataset_info(self, dataset_id: str) -> dict:
        """Get dataset metadata: title, description, organization, resources."""
        return datasets.get_dataset_info(self.base_url, dataset_id, self.timeout)

    def list_dataset_resources(self, dataset_id: str) -> dict:
        """List all resources (files) in a dataset with metadata."""
        return datasets.list_dataset_resources(self.base_url, dataset_id, self.timeout)

    def get_resource_info(self, resource_id: str) -> dict:
        """Get resource metadata: format, size, URL."""
        return resources.get_resource_info(self.base_url, resource_id, self.timeout)

    def download_resource(
        self, resource_id: str, max_rows: int | None = None, max_size_mb: int = 500
    ) -> dict:
        """Download and parse a resource (CSV, JSON, JSONL). Supports parquet."""
        return resources.download_resource(
            self.base_url, resource_id, self.timeout, max_rows, max_size_mb
        )

    def search_dataservices(self, query: str, page: int = 1, page_size: int = 20) -> dict:
        """Search dataservices (API catalog) by keywords."""
        return datasets.search_dataservices(self.base_url, query, page, page_size, self.timeout)

    def get_dataservice_info(self, dataservice_id: str) -> dict:
        """Get dataservice metadata."""
        return datasets.get_dataservice_info(self.base_url, dataservice_id, self.timeout)


def get_openai_tools(include_oll: bool = False) -> list[dict]:
    """
    Return OpenAI tool schemas for function calling. Use with LLM agents.

    Args:
        include_oll: Include OLL rent tools (requires OLL data loaded).

    Returns:
        List of tool definitions compatible with OpenAI API.
    """
    from datagouv_client.tools.schemas import OPENAI_TOOLS

    tools = list(OPENAI_TOOLS)
    if include_oll:
        from datagouv_client.tools.schemas import OPENAI_TOOLS_OLL

        tools.extend(OPENAI_TOOLS_OLL)
    return tools


def run_tool(name: str, arguments: dict, client: DatagouvClient | None = None) -> dict:
    """
    Execute a tool by name. For use in agent loops.

    Args:
        name: Tool name (e.g. search_datasets, get_dataset_info).
        arguments: Tool arguments.
        client: DatagouvClient instance. Creates one if None.

    Returns:
        Tool result as dict.
    """
    client = client or DatagouvClient()
    return _TOOL_RUNNERS[name](client, arguments)


def register_tool(name: str, runner: Callable) -> None:
    """Register a custom tool runner. Extend the client with new capabilities."""
    _TOOL_RUNNERS[name] = runner


def _run_search_datasets(client: DatagouvClient, args: dict) -> dict:
    return client.search_datasets(
        args["query"],
        args.get("page", 1),
        args.get("page_size", 20),
    )


def _run_get_dataset_info(client: DatagouvClient, args: dict) -> dict:
    return client.get_dataset_info(args["dataset_id"])


def _run_list_resources(client: DatagouvClient, args: dict) -> dict:
    return client.list_dataset_resources(args["dataset_id"])


def _run_get_resource_info(client: DatagouvClient, args: dict) -> dict:
    return client.get_resource_info(args["resource_id"])


def _run_download_resource(client: DatagouvClient, args: dict) -> dict:
    return client.download_resource(
        args["resource_id"],
        max_rows=args.get("max_rows"),
        max_size_mb=args.get("max_size_mb", 500),
    )


def _run_search_dataservices(client: DatagouvClient, args: dict) -> dict:
    return client.search_dataservices(
        args["query"],
        args.get("page", 1),
        args.get("page_size", 20),
    )


def _run_get_dataservice_info(client: DatagouvClient, args: dict) -> dict:
    return client.get_dataservice_info(args["dataservice_id"])


_TOOL_RUNNERS: dict[str, Callable] = {
    "search_datasets": _run_search_datasets,
    "get_dataset_info": _run_get_dataset_info,
    "list_dataset_resources": _run_list_resources,
    "get_resource_info": _run_get_resource_info,
    "download_resource": _run_download_resource,
    "search_dataservices": _run_search_dataservices,
    "get_dataservice_info": _run_get_dataservice_info,
}
