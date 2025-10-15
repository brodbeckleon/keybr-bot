import asyncio
import random
import time
from urllib.parse import urlparse
import os

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Config:
AUTH_FILE = "auth_state.json"

surroundingKeysMap= {
    'q': ['w'],
    'w': ['q', 'e'],
    'e': ['w', 'r'],
    'r': ['e', 't'],
    't': ['r', 'z'],
    'z': ['t', 'u'],
    'u': ['z', 'i'],
    'i': ['u', 'o'],
    'o': ['i', 'p'],
    'p': ['o'],

    # Second row
    'a': ['s'],
    's': ['a', 'd'],
    'd': ['s', 'f'],
    'f': ['d', 'g'],
    'g': ['f', 'h'],
    'h': ['g', 'j'],
    'j': ['h', 'k'],
    'k': ['j', 'l'],
    'l': ['k'],

    # Third row
    'y': ['x'],
    'x': ['y', 'c'],
    'c': ['x', 'v'],
    'v': ['c', 'b'],
    'b': ['v', 'n'],
    'n': ['b', 'm'],
    'm': ['n'],
}

def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36" # RPi agent
    ]
    return random.choice(user_agents)

async def random_pause():
    await asyncio.sleep(random.uniform(0.5, 1.5))

async def close_tutorial_popup(page):
    try:
        await page.wait_for_selector("text=Next", timeout=3000)
        print("Walking through the tutorial")
        while True:
            try:
                await page.click("text=Next", timeout=1000)
                print("Clicked 'Next'")
                await random_pause()
            except PlaywrightTimeoutError:
                try:
                    await page.click("text=Close", timeout=1000)
                    print("Tutorial closed")
                    break
                except PlaywrightTimeoutError:
                    print("No 'Next' or 'Close' found — exiting loop.")
                    break
    except PlaywrightTimeoutError:
        print("No Tutorial detected")

async def get_typing_pause():
    return random.uniform(30, 300)

async def get_false_key(char):
    if char in surroundingKeysMap:
        possible_false_keys = surroundingKeysMap[char]
        return random.choice(possible_false_keys)
    return None

async def type_text(locator, page):
    text_content = await locator.inner_text()
    text_content = text_content.replace("", " ")
    print(f"\n--- Text to type ---\n{text_content}\n--------------------")

    for i, char in enumerate(text_content):
        is_false_press = random.random() < 0.05
        if is_false_press and char.isalpha() and char in surroundingKeysMap:
            false_key = await get_false_key(char)
            if false_key:
                await page.keyboard.type(false_key, delay=await get_typing_pause())
                await asyncio.sleep(random.uniform(0.05, 0.3)) # Pause after mistype
                await page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.05, 0.1)) # Pause after correction

        await page.keyboard.type(char, delay=await get_typing_pause())

async def main():
    if not os.path.exists(AUTH_FILE):
        print(f"Error: Auth file '{AUTH_FILE}' not found.")
        print("Please run 'create_auth.py' first to log in and create the file.")
        return

    blocked_domains = [
        "googlesyndication.com", "google-analytics.com", "doubleclick.net",
        "adservice.google.com", "googletagservices.com", "c.amazon-adsystem.com",
        "ads.pubmatic.com",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            storage_state=AUTH_FILE,
            user_agent=random_user_agent()
        )

        await context.route(
            lambda url: urlparse(url).hostname and any(domain in urlparse(url).hostname for domain in blocked_domains),
            lambda route: route.abort()
        )

        page = await context.new_page()
        await page.goto("https://www.keybr.com/", wait_until="networkidle")
        await close_tutorial_popup(page)

        training_minutes = random.randint(7, 30)
        print(f"Starting a training session for {training_minutes} minutes.")

        locator = page.locator("main > section > div:nth-of-type(2) > div > div")
        await locator.wait_for(state="visible")
        await locator.click()
        print("Clicked on the typing area")

        start_time = time.time()
        duration_seconds = training_minutes * 60

        while (time.time() - start_time) < duration_seconds:
            remaining_seconds = duration_seconds - (time.time() - start_time)
            print(f"Time remaining: {int(remaining_seconds / 60)} minutes")
            await type_text(locator, page)
            await random_pause()

        print(f"Completed {training_minutes} minutes of training.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
