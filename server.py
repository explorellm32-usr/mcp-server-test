import os
import json
import asyncio
import re
from curl_cffi.requests import AsyncSession
from datetime import datetime
from bs4 import BeautifulSoup
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("AmazonProductIntelligenceAgent")

DB_FILE = "amazon_products_db.json"

# A realistic browser User-Agent to avoid being blocked by Amazon
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

@mcp.tool()
async def fetch_amazon_product(asin: str) -> str:
    """
    Asynchronously fetches product intelligence from an Amazon product page.
    Extracts: product title, price, star rating, review count, and top 5 customer reviews.
    
    Args:
        asin: The Amazon Standard Identification Number (e.g., 'B08N5WRWNW' for Echo Dot).
    Returns:
        A structured intelligence report as a JSON string.
    """
    url = f"https://www.amazon.in/dp/{asin}"
    try:
        async with AsyncSession(impersonate="chrome", timeout=20) as client:
            # Fetch sequentially with a delay to avoid triggering bot detection
            product_resp = await client.get(url)
            await asyncio.sleep(1.5)  # Pause to mimic human behavior
            
            reviews_url = f"https://www.amazon.in/product-reviews/{asin}?pageNumber=1"
            reviews_resp = await client.get(reviews_url)

        # --- Parse Product Page ---
        soup = BeautifulSoup(product_resp.text, "html.parser")
        
        title = soup.select_one("#productTitle")
        title = title.get_text(strip=True) if title else "N/A"

        price = soup.select_one(".a-price .a-offscreen")
        price = price.get_text(strip=True) if price else "N/A"

        rating = soup.select_one("span[data-hook='rating-out-of-text']")
        if not rating:
            rating = soup.select_one("#acrPopover")
        rating = rating.get_text(strip=True) if rating else "N/A"
        
        review_count = soup.select_one("#acrCustomerReviewText")
        review_count = review_count.get_text(strip=True) if review_count else "N/A"

        # --- Parse Reviews Page ---
        rev_soup = BeautifulSoup(reviews_resp.text, "html.parser")
        review_blocks = rev_soup.select("[data-hook='review']")[:5]
        reviews = []
        for block in review_blocks:
            r_title = block.select_one("[data-hook='review-title'] span:last-child")
            r_body  = block.select_one("[data-hook='review-body'] span")
            r_stars = block.select_one("[data-hook='review-star-rating'] span")
            reviews.append({
                "title":  r_title.get_text(strip=True) if r_title else "N/A",
                "body":   r_body.get_text(strip=True)[:300] if r_body else "N/A",
                "rating": r_stars.get_text(strip=True) if r_stars else "N/A",
            })

        report = {
            "asin":          asin,
            "title":         title,
            "price":         price,
            "avg_rating":    rating,
            "review_count":  review_count,
            "top_reviews":   reviews,
            "source_url":    url,
            "fetched_at":    datetime.now().isoformat(),
        }
        return json.dumps(report, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "asin": asin})


@mcp.tool()
def manage_product_database(action: str, asin: str, data: str = None) -> str:
    """
    CRUD operations for the local Amazon product intelligence JSON database.
    
    Args:
        action:  'create', 'read', 'update', or 'delete'
        asin:    The product ASIN (unique key in the database)
        data:    JSON string of product data (required for create/update)
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
            db[asin] = parsed
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            return f"✅ Successfully {action}d product record for ASIN '{asin}'."

        elif action == "read":
            if asin in db:
                return json.dumps(db[asin], indent=2)
            return f"⚠️ No record found for ASIN '{asin}'."

        elif action == "delete":
            if asin in db:
                del db[asin]
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
                return f"🗑️ Successfully deleted record for ASIN '{asin}'."
            return f"⚠️ No record found for ASIN '{asin}' to delete."

        else:
            return f"❌ Invalid action '{action}'. Choose from: create, read, update, delete."

    except Exception as e:
        return f"Database error: {e}"


@mcp.tool(app=True)
def show_product_dashboard(asin: str):
    """
    Reads a product record from the database and renders a rich
    Prefab UI product intelligence dashboard — including star ratings,
    pricing, review count, and individual customer reviews.
    """
    from prefab_ui.components import Card, Text, Container, Badge

    def star_bar(rating_str: str) -> str:
        """Convert '4.2 out of 5 stars' to a visual ★ bar."""
        match = re.search(r"([\d.]+)", rating_str or "")
        if match:
            val = float(match.group(1))
            filled = round(val)
            return "★" * filled + "☆" * (5 - filled) + f"  {val}/5"
        return rating_str or "N/A"

    try:
        if not os.path.exists(DB_FILE):
            with Container(className="p-8"):
                with Card(title="⚠️ Database Empty"):
                    Text("Run the agent first to fetch and store product data.", className="text-gray-500")
            return

        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)

        if asin not in db:
            with Container(className="p-8"):
                with Card(title=f"⚠️ No data for ASIN: {asin}"):
                    Text("Run the agent pipeline to fetch this product first.", className="text-gray-500")
            return

        p = db[asin]
        reviews = p.get("top_reviews", [])

        # ── Dashboard Layout ─────────────────────────────────────────────
        with Container(className="p-6 bg-gray-50 min-h-screen font-sans"):

            # Hero card
            with Card(
                title=f"🛒 {p.get('title', 'Unknown Product')}",
                description=f"ASIN: {asin}  •  Source: {p.get('source_url', 'amazon.in')}",
                className="max-w-4xl mx-auto shadow-2xl border-t-4 border-orange-500 bg-white mb-6"
            ):
                # Key metrics row
                with Container(className="flex gap-6 flex-wrap mt-2 mb-4"):
                    Text(f"💰 Price: {p.get('price', 'N/A')}", className="text-2xl font-bold text-green-700")
                    Text(star_bar(p.get('avg_rating', '')),   className="text-xl text-yellow-500 font-semibold")
                    Text(f"📝 {p.get('review_count', 'N/A')} ratings", className="text-lg text-gray-600")

                Text(
                    f"Last fetched: {p.get('fetched_at', 'N/A')}  |  DB updated: {p.get('db_last_updated', 'N/A')}",
                    className="text-xs text-gray-400 italic mb-4"
                )

            # Reviews section
            with Card(
                title="💬 Top Customer Reviews",
                description="Auto-scraped from Amazon India",
                className="max-w-4xl mx-auto shadow-lg bg-white"
            ):
                if not reviews:
                    Text("No reviews found.", className="text-gray-400 italic")
                else:
                    for i, review in enumerate(reviews, 1):
                        with Container(className="border-b border-gray-100 pb-4 mb-4 last:border-0 last:mb-0"):
                            with Container(className="flex items-center gap-3 mb-1"):
                                Text(f"Review #{i}", className="font-bold text-gray-800 text-sm")
                                Text(star_bar(review.get('rating', '')), className="text-yellow-500 text-sm")
                            Text(review.get('title', ''), className="font-semibold text-gray-700 mb-1")
                            Text(review.get('body', ''),  className="text-gray-600 text-sm leading-relaxed")

    except Exception as e:
        with Card(title="❌ Dashboard Error", className="border-red-500 max-w-4xl mx-auto"):
            Text(f"Failed to generate dashboard: {str(e)}", className="text-red-500 font-mono text-sm")


if __name__ == "__main__":
    mcp.run()

