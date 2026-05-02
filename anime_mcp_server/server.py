import os
import json
from fastmcp import FastMCP
import httpx
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("AnimeIntelligenceAgent")

DB_FILE = "anime_vault.json"

@mcp.tool()
async def fetch_anime_intelligence(query: str) -> str:
    """
    Asynchronously fetches anime intelligence from the Jikan API (MyAnimeList).
    Extracts: title, score, episodes, synopsis, and status.
    
    Args:
        query: The name of the anime to search for (e.g., 'Attack on Titan').
    Returns:
        A structured intelligence report as a JSON string.
    """
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("data"):
                return json.dumps({"error": f"No anime found for query: {query}"})
                
            anime = data["data"][0]
            
            report = {
                "id": str(anime.get("mal_id")),
                "title": anime.get("title"),
                "title_english": anime.get("title_english") or anime.get("title"),
                "score": anime.get("score", "N/A"),
                "episodes": anime.get("episodes", "N/A"),
                "status": anime.get("status", "Unknown"),
                "synopsis": anime.get("synopsis", "No synopsis available."),
                "fetched_at": datetime.now().isoformat(),
            }
            return json.dumps(report, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "query": query})


@mcp.tool()
def manage_anime_vault(action: str, anime_id: str, data: str = None) -> str:
    """
    CRUD operations for the local Anime Vault JSON database.
    
    Args:
        action:  'create', 'read', 'update', or 'delete'
        anime_id: The anime's MyAnimeList ID (unique key in the database)
        data:    JSON string of anime data (required for create/update)
    Returns:
        A status message or the stored JSON data.
    """
    try:
        # Initialise DB file if it doesn't exist
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)

        action = action.lower().strip()

        if action in ("create", "update"):
            if not data:
                return "Error: 'data' parameter is required for create/update."
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                parsed = {"raw": data}
            parsed["db_last_updated"] = datetime.now().isoformat()
            db[anime_id] = parsed
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            return f"✅ Successfully {action}d anime record for ID '{anime_id}'."

        elif action == "read":
            if anime_id in db:
                return json.dumps(db[anime_id], indent=2)
            return f"⚠️ No record found for ID '{anime_id}'."

        elif action == "delete":
            if anime_id in db:
                del db[anime_id]
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
                return f"🗑️ Successfully deleted record for ID '{anime_id}'."
            return f"⚠️ No record found for ID '{anime_id}' to delete."

        else:
            return f"❌ Invalid action '{action}'. Choose from: create, read, update, delete."

    except Exception as e:
        return f"Database error: {e}"


@mcp.tool(app=True)
def show_anime_dashboard(anime_id: str):
    """
    Reads an anime record from the database and renders a rich
    Prefab UI anime intelligence dashboard — including score, episodes,
    and a detailed synopsis.
    """
    from prefab_ui.app import PrefabApp
    from prefab_ui.components import (
        Card, CardContent, CardHeader,
        Column, Row, Grid,
        Heading, H3, Text, Muted, Small, Badge,
    )

    try:
        if not os.path.exists(DB_FILE):
            with PrefabApp() as app:
                with Column(gap=4, css_class="p-8"):
                    Heading("⚠️ Vault Empty")
                    Text("Run the agent first to fetch and store anime data.")
            return app

        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)

        if anime_id not in db:
            with PrefabApp() as app:
                with Column(gap=4, css_class="p-8"):
                    Heading(f"⚠️ No data for ID: {anime_id}")
                    Text("Run the agent pipeline to fetch this anime first.")
            return app

        p = db[anime_id]

        # ── Dashboard Layout ─────────────────────────────────────────────
        with PrefabApp() as app:
            with Column(gap=4, css_class="p-6"):
                Heading(f"🎬 {p.get('title_english', 'Unknown Anime')}")
                Muted(f"MAL ID: {anime_id}  •  Status: {p.get('status', 'Unknown')}")

                # Key metrics
                with Row(gap=2):
                    Badge(f"⭐ Score: {p.get('score', 'N/A')}")
                    Badge(f"📺 Episodes: {p.get('episodes', 'N/A')}")

                # Synopsis card
                with Card():
                    with CardHeader():
                        H3("Synopsis")
                    with CardContent():
                        Text(p.get('synopsis', 'No synopsis available.'))

                # Metadata
                Small(
                    f"Fetched: {p.get('fetched_at', 'N/A')[:10]}  |  "
                    f"DB updated: {p.get('db_last_updated', 'N/A')[:10]}"
                )

        return app

    except Exception as e:
        with PrefabApp() as app:
            with Column(gap=4, css_class="p-8"):
                Heading("❌ Dashboard Error")
                Text(f"Failed to generate dashboard: {str(e)}")
        return app


if __name__ == "__main__":
    mcp.run()
