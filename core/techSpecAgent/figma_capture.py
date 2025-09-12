import os, asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

FIGMA_FILE_URL = os.getenv("FIGMA_FILE_URL")

#FIGMA_FILE_URL = "https://www.figma.com/design/ZC6WcE8iXWma7RESnZdo65/Sample?node-id=37-2&p=f&t=PPAFTWzPI6hLZYSy-0"

WAIT_SELECTOR = os.getenv("FIGMA_WAIT_SELECTOR", "[data-testid='canvas_zoom_controls']")
VIEW_W = int(os.getenv("FIGMA_VIEWPORT_WIDTH", "1600"))
VIEW_H = int(os.getenv("FIGMA_VIEWPORT_HEIGHT", "1000"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "TechSpecOutputs")

async def capture_figma_screenshot() -> str:
    if not FIGMA_FILE_URL:
        raise RuntimeError("FIGMA_FILE_URL is required in .env")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "figma_screen.png")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.set_viewport_size({"width": VIEW_W, "height": VIEW_H})
        await page.goto(FIGMA_FILE_URL, wait_until="domcontentloaded")
        try:
            await page.wait_for_selector(WAIT_SELECTOR, timeout=30000)
        except:
            pass
        await page.screenshot(path=out_path, full_page=True)
        await browser.close()
    return out_path

def capture_sync() -> str:
    return asyncio.run(capture_figma_screenshot())
