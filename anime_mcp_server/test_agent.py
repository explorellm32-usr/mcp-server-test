"""
Anime Intelligence Agent - Test Runner
=======================================
This script simulates what an LLM agent does when it receives the prompt.
It calls the MCP tools in the correct order:
  1. fetch_anime_intelligence  --> Internet fetch (Jikan/MAL API)
  2. manage_anime_vault        --> CRUD save to local anime_vault.json
  3. show_anime_dashboard      --> Prefab UI render

HOW TO RUN:
  1. Make sure you are inside the 'anime_mcp_server' folder:
       cd anime_mcp_server
  2. Install dependencies:
       pip install -r requirements.txt
  3. Run this script:
       python test_agent.py
  4. Open the Prefab dashboard URL printed in the console.

THE PROMPT this agent is responding to:
  "Find details about the anime 'Attack on Titan', save those details
   in my local vault, and show it to me on a dashboard."
"""

import asyncio
import json
from server import fetch_anime_intelligence, manage_anime_vault, show_anime_dashboard


PROMPT_ANIME = "Attack on Titan"   # ← Change this to any anime you want!


async def run_agent():
    print("=" * 60)
    print("🤖 Anime Intelligence Agent - Starting Agentic Loop")
    print("=" * 60)
    print(f'\n📨 USER PROMPT: "Find details about \"{PROMPT_ANIME}\", save it to my vault, and show me the dashboard."\n')

    # ── STEP 1: Internet Fetch ────────────────────────────────────────
    print("─" * 60)
    print(f"🌐 [Tool Call #1] fetch_anime_intelligence(query='{PROMPT_ANIME}')")
    print("─" * 60)
    result_json = await fetch_anime_intelligence(PROMPT_ANIME)
    result = json.loads(result_json)

    if "error" in result:
        print(f"❌ Fetch failed: {result['error']}")
        return

    anime_id = result["id"]
    print(f"✅ Fetched: '{result.get('title_english')}' | MAL ID: {anime_id}")
    print(f"   Score: {result.get('score')} | Episodes: {result.get('episodes')} | Status: {result.get('status')}")
    print(f"   Synopsis: {result.get('synopsis', '')[:120]}...")

    # ── STEP 2: CRUD Save to Local Vault ─────────────────────────────
    print()
    print("─" * 60)
    print(f"💾 [Tool Call #2] manage_anime_vault(action='create', anime_id='{anime_id}')")
    print("─" * 60)
    save_status = manage_anime_vault(
        action="create",
        anime_id=anime_id,
        data=result_json,
    )
    print(f"   {save_status}")

    # ── STEP 3: Prefab UI Dashboard ───────────────────────────────────
    print()
    print("─" * 60)
    print(f"🎨 [Tool Call #3] show_anime_dashboard(anime_id='{anime_id}')")
    print("─" * 60)
    show_anime_dashboard(anime_id)
    print("   ✅ Dashboard rendered via Prefab UI.")

    print()
    print("=" * 60)
    print("🏁 Agentic Loop Complete! All 3 tools used successfully.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_agent())
