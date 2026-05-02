import asyncio
from server import fetch_amazon_product

async def run_test():
    print("🔍 Fetching data for Amazon Echo Dot (ASIN: B08N5WRWNW)...")
    print("⏳ Please wait, scraping in progress...\n")
    
    # This directly calls your tool
    result = await fetch_amazon_product("B08N5WRWNW  ")
    
    print("✅ --- RESULTS --- ✅\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(run_test())
