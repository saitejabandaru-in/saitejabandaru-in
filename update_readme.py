import os
import re
import json
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# Configuration
TOKEN = os.environ.get("GITHUB_TOKEN")
README_PATH = "README.md"

ITEMS = [
    {"repo": "qdrant/qdrant", "number": 1264, "type": "pr", "desc": "Vector search engine improvement"},
    {"repo": "run-llama/llama_index", "number": 22343, "type": "pr", "desc": "MinioReader basename collision fix"},
    {"repo": "chroma-core/chroma", "number": 7432, "type": "pr", "desc": "Embedding search improvement"},
    {"repo": "logspace-ai/langflow", "number": 14051, "type": "pr", "desc": "Workflow engine enhancement"},
    {"repo": "lancedb/lancedb", "number": 3661, "type": "pr", "desc": "Retrieval pipeline fix"},
    {"repo": "milvus-io/pymilvus", "number": 3686, "type": "pr", "desc": "Python SDK improvement"},
    {"repo": "explodinggradients/ragas", "number": 2850, "type": "pr", "desc": "Evaluation framework fix"},
    {"repo": "cleanlab/cleanlab", "number": 1321, "type": "pr", "desc": "Data-centric AI enhancement"},
    {"repo": "public-apis/public-apis", "number": 6592, "type": "issue", "desc": "Reported 5 broken API links"}
]

def make_request(url):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "readme-updater-bot"
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_item_status(item):
    repo = item["repo"]
    number = item["number"]
    
    if item["type"] == "pr":
        # Fetch PR details
        pr_data = make_request(f"https://api.github.com/repos/{repo}/pulls/{number}")
        if not pr_data:
            return "🔍 Under Review"
            
        if pr_data.get("merged"):
            return "✅ **Merged**"
            
        if pr_data.get("state") == "closed":
            return "🏁 Closed"
            
        # Check reviews to see if approved
        reviews = make_request(f"https://api.github.com/repos/{repo}/pulls/{number}/reviews")
        if reviews:
            for r in reviews:
                if r.get("state") == "APPROVED":
                    return "✅ Approved"
                    
        return "🔍 Under Review"
        
    else:
        # Fetch issue details
        issue_data = make_request(f"https://api.github.com/repos/{repo}/issues/{number}")
        if not issue_data:
            return "📋 Issue Filed"
            
        if issue_data.get("state") == "closed":
            return "✅ Resolved"
            
        return "📋 Issue Filed"

def main():
    print("Fetching latest statuses from GitHub API...")
    rows = []
    for item in ITEMS:
        status = get_item_status(item)
        repo_link = f"[{item['repo']}](https://github.{item['repo']})"
        if item["type"] == "pr":
            item_link = f"[#{item['number']}](https://github.com/{item['repo']}/pull/{item['number']})"
        else:
            item_link = f"[#{item['number']}](https://github.com/{item['repo']}/issues/{item['number']})"
            
        rows.append(f"| **[{item['repo']}](https://github.com/{item['repo']})** | {item_link} | {item['desc']} | {status} |")
        print(f"{item['repo']}#{item['number']} -> {status}")
        
    table_content = "\n".join(rows)
    table_markdown = f"""<!-- START_OSS_TABLE -->
| Repository | PR | Description | Status |
|:-----------|:---|:------------|:-------|
{table_content}
<!-- END_OSS_TABLE -->"""

    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.")
        return
        
    with open(README_PATH, "r") as f:
        content = f.read()
        
    pattern = r"<!-- START_OSS_TABLE -->.*?<!-- END_OSS_TABLE -->"
    updated_content = re.sub(pattern, table_markdown, content, flags=re.DOTALL)
    
    with open(README_PATH, "w") as f:
        f.write(updated_content)
        
    print("README.md updated successfully!")

if __name__ == "__main__":
    main()
