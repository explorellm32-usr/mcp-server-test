# Amazon Product Intelligence Agent

An autonomous Model Context Protocol (MCP) server that scrapes Amazon product details and reviews, manages local JSON database storage, and visualizes intelligence data using a rich Prefab UI dashboard.

## Features

- **Asynchronous Scraping**: Uses `httpx` and `BeautifulSoup4` to concurrently fetch product metadata (price, title, review count, average rating) and top customer reviews from Amazon.
- **Local Persistence**: Provides full CRUD operations for managing product intelligence data in a local JSON database.
- **Rich Dashboard**: Generates a beautiful Prefab UI dashboard to visualize the gathered intelligence.
- **MCP Standard**: Fully compatible with any Model Context Protocol client using `fastmcp`.

## Prerequisites

- Python 3.12+ (64-bit recommended)
- Node.js (for the MCP Inspector)

## Installation

### Local Setup
1. Clone or download the repository.
2. Open a terminal in the project directory.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR: source venv/Scripts/activate  # On Windows Git Bash
   # OR: .\venv\Scripts\activate # On Windows PowerShell
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Online Setup (Replit / GitHub Codespaces)
If you cannot install the dependencies locally, you can use a cloud IDE:
1. Upload the files to Replit or a GitHub Codespace.
2. Run the installation command in the provided terminal: `pip install -r requirements.txt`.

## Usage & Testing

The easiest way to test the agent's capabilities is using the official MCP Inspector.

1. Start the inspector:
   ```bash
   npx @modelcontextprotocol/inspector python server.py
   ```
2. Open the provided localhost URL in your browser.
3. Navigate to the **Tools** tab to test the following functions:
   - `fetch_amazon_product`: Use an ASIN (like `B08N5WRWNW`) to scrape data.
   - `manage_product_database`: Save the scraped JSON data to your local database.
   - `show_product_dashboard`: View the generated UI for your saved ASIN.

Ex:
https://www.amazon.in/Amazon-Brand-Presto-Oxo-Biodegradable-Garbage/dp/B0821PN8L4/ref=zg_bs_c_kitchen_d_sccl_1/259-9731870-4167526?pd_rd_w=cfXa7&content-id=amzn1.sym.b908f532-cbe7-4274-8b24-b671acc58bd2&pf_rd_p=b908f532-cbe7-4274-8b24-b671acc58bd2&pf_rd_r=F8ZX5X2ZT11NKKGT6PXC&pd_rd_wg=wuSNK&pd_rd_r=b24b1a45-e140-4aad-bc3c-4f47f6ec477e&pd_rd_i=B0821PN8L4&th=1

ASIN is B0821PN8L4

## Integrating with an LLM Client

Add the server to your MCP-compatible client (e.g., Claude Desktop) configuration:

```json
{
  "mcpServers": {
    "amazon-intelligence": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```
