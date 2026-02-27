"""Simple usage of datagouv-mcp-client."""

from datagouv_client import DatagouvClient

def main():
    client = DatagouvClient()

    # Search datasets
    result = client.search_datasets("loyers", page_size=5)
    print("Datasets found:", result["total"])
    for d in result["datasets"][:3]:
        print(f"  - {d['title']} (id: {d['id']})")

    # Get dataset info
    dataset_id = "56fd8e8788ee387079c352f7"  # OLL national
    info = client.get_dataset_info(dataset_id)
    print(f"\nDataset: {info['title']}")
    print(f"Resources: {info['resources_count']}")

    # List resources
    resources = client.list_dataset_resources(dataset_id)
    for r in resources["resources"][:3]:
        print(f"  - {r['title']} ({r['format']})")

if __name__ == "__main__":
    main()
