# Anime Intelligence Agent (MCP Server)

An autonomous Model Context Protocol (MCP) server that fetches anime details from MyAnimeList (via the Jikan API), manages a local JSON database, and visualizes intelligence data using a rich Prefab UI dashboard.

## Features

- **Asynchronous Fetching**: Uses `httpx` to fetch anime metadata (title, score, episodes, status, synopsis) from the Jikan API.
- **Local Persistence**: Full CRUD operations for managing anime data in a local `anime_vault.json` database.
- **Rich Dashboard**: Generates a beautiful Prefab UI dashboard to visualize anime intelligence.
- **MCP Standard**: Fully compatible with any Model Context Protocol client using `fastmcp`.

## Tools

| Tool | Description |
|---|---|
| `fetch_anime_intelligence` | Fetches anime data from MyAnimeList via the Jikan API |
| `manage_anime_vault` | CRUD operations (create, read, update, delete) on the local JSON database |
| `show_anime_dashboard` | Renders a visual Prefab UI dashboard for a saved anime |

## Prerequisites

- Python 3.12+
- Node.js (for the MCP Inspector)

## Installation (macOS)

1. Clone or download the repository.
2. Open a terminal and navigate to the project root:
   ```bash
   cd mcp-server-test
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r anime_mcp_server/requirements.txt
   ```

## Usage & Testing

There are **two tools** you'll use, each for a different purpose:

| Purpose | Command |
|---|---|
| **Test tools** (fetch, save, read, delete) | `npx @modelcontextprotocol/inspector` |
| **View Prefab UI dashboard** | `fastmcp dev apps` |

### Step 1: Fetch & Save Data (MCP Inspector)

1. Navigate to the `anime_mcp_server` directory:
   ```bash
   cd anime_mcp_server
   ```
2. Start the MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector ../venv/bin/python server.py
   ```
3. Open the provided localhost URL (usually http://localhost:6274) in your browser.
4. Go to the **Tools** tab.
5. Click **`fetch_anime_intelligence`**, enter a query (e.g., `Naruto`), and click **Run**.
6. Copy the JSON result.
7. Click **`manage_anime_vault`**, fill in:
   - **action**: `create`
   - **anime_id**: the `id` from the fetched result (e.g., `20`)
   - **data**: paste the JSON from step 6
8. Click **Run** — you should see `✅ Successfully created...`.
9. Stop the inspector with `Ctrl+C`.

### Step 2: View the Dashboard (Prefab UI)

1. Launch the FastMCP Apps viewer:
   ```bash
   ../venv/bin/fastmcp dev apps server.py
   ```
2. Open http://localhost:8080 in your browser.
3. Select **`show_anime_dashboard`**.
4. Enter the `anime_id` (e.g., `20`) and click **Launch**.
5. The visual dashboard will render with the anime's title, score, episodes, and synopsis!

### Automated Test Script

You can also run `test_agent.py` which automates all 3 steps (fetch → save → dashboard):
```bash
../venv/bin/python test_agent.py
```

## Sample Anime to Test

| Anime | Query |
|---|---|
| Naruto | `Naruto` |
| Death Note | `Death Note` |
| Attack on Titan | `Attack on Titan` |
| Fullmetal Alchemist: Brotherhood | `Fullmetal Alchemist Brotherhood` |
| Demon Slayer | `Demon Slayer` |
| Jujutsu Kaisen | `Jujutsu Kaisen` |
| Spy × Family | `Spy x Family` |
| One Piece | `One Piece` |
| Dragon Ball Z | `Dragon Ball Z` |
| Hunter × Hunter | `Hunter x Hunter` |

## Integrating with an LLM Client (Claude Desktop)

To chat with an AI that uses your tools automatically, add the server to your Claude Desktop config:

1. Open the config file:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
2. Add the following:
   ```json
   {
     "mcpServers": {
       "anime-intelligence": {
         "command": "/Users/venkat/Documents/ERA/mcp-server-test/venv/bin/python",
         "args": [
           "/Users/venkat/Documents/ERA/mcp-server-test/anime_mcp_server/server.py"
         ]
       }
     }
   }
   ```
3. Restart Claude Desktop.
4. You can now prompt Claude:
   > "Find details about Death Note, save it to my vault, and show me the dashboard."

## Project Structure

```
anime_mcp_server/
├── server.py           # MCP server with 3 tools
├── test_agent.py       # Automated test script (runs all 3 tools)
├── requirements.txt    # Python dependencies
├── anime_vault.json    # Local JSON database (auto-created)
└── README.md           # This file
```
