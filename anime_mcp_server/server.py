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
    from prefab_ui.components import Card, Text, Container, Badge

    try:
        if not os.path.exists(DB_FILE):
            with Container(className="p-8"):
                with Card(title="⚠️ Vault Empty"):
                    Text("Run the agent first to fetch and store anime data.", className="text-gray-500")
            return

        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)

        if anime_id not in db:
            with Container(className="p-8"):
                with Card(title=f"⚠️ No data for ID: {anime_id}"):
                    Text("Run the agent pipeline to fetch this anime first.", className="text-gray-500")
            return

        p = db[anime_id]

        # ── Dashboard Layout ─────────────────────────────────────────────
        with Container(className="p-8 bg-slate-900 min-h-screen font-sans"):

            # Hero card
            with Card(
                title=f"🎬 {p.get('title_english', 'Unknown Anime')}",
                description=f"MAL ID: {anime_id}  •  Status: {p.get('status', 'Unknown')}",
                className="max-w-4xl mx-auto shadow-2xl border-t-4 border-purple-500 bg-slate-800 text-white mb-6"
            ):
                # Key metrics row
                with Container(className="flex gap-4 flex-wrap mt-4 mb-6"):
                    Badge(f"⭐ Score: {p.get('score', 'N/A')}", className="bg-yellow-500 text-black px-4 py-2 rounded-full font-bold text-sm")
                    Badge(f"📺 Episodes: {p.get('episodes', 'N/A')}", className="bg-purple-600 text-white px-4 py-2 rounded-full font-bold text-sm")

                with Container(className="bg-slate-700 p-4 rounded-lg mb-4"):
                    Text("Synopsis", className="text-xl font-bold text-purple-300 mb-2")
                    Text(p.get('synopsis', 'No synopsis available.'), className="text-slate-200 text-sm leading-relaxed")

                Text(
                    f"Fetched: {p.get('fetched_at', 'N/A')[:10]}  |  DB updated: {p.get('db_last_updated', 'N/A')[:10]}",
                    className="text-xs text-slate-400 italic mt-4 border-t border-slate-600 pt-2"
                )

    except Exception as e:
        with Card(title="❌ Dashboard Error", className="border-red-500 max-w-4xl mx-auto"):
            Text(f"Failed to generate dashboard: {str(e)}", className="text-red-500 font-mono text-sm")


if __name__ == "__main__":
    mcp.run()
