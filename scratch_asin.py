import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

async def main():
    asin = "B0821PN8L4"
    url = f"https://www.amazon.in/dp/{asin}"
    print(f"Fetching {url}...")
    
    async with AsyncSession(impersonate="chrome", timeout=20) as client:
        resp = await client.get(url)
        print("Status:", resp.status_code)
        
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one("#productTitle")
        
        if title:
            print("Title:", title.get_text(strip=True))
        else:
            print("Title: N/A (Probably blocked or CAPTCHA)")
            if "captcha" in resp.text.lower() or "robot" in resp.text.lower():
                print("DETECTED: CAPTCHA page")
            elif resp.status_code == 404:
                print("DETECTED: 404 Not Found")
            else:
                print("Page sample:", resp.text[:500])

if __name__ == "__main__":
    asyncio.run(main())
