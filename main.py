import asyncio
import random
import time
from urllib.parse import urlparse

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Config:
mailAdress = "Z125513@shibaura-it.ac.jp"
trainingTime = 0
attempts = 5

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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    ]
    return random.choice(user_agents)

async def login(page):
    page.goto('https://www.keybr.com/login', wait_until='load')

    await page.click("text=Sign-In", timeout=1000)
    await random_pause()

    await page.get_by_placeholder("Your e-mail address").fill(mailAdress, timeout=1000)
    print("filled in the mail adress")

    await random_pause()
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.click("text=Send a sign-in link", timeout=1000)
    print("Requested a Sign-in link")

    loginLink: str = input("Enter the login link: ")

    await page.goto(loginLink, timeout=1000)

async def random_pause():
    random_pause = random.uniform(0.5, 2)
    time.sleep(random_pause)

async def close_tutorial_popup(page):
    """
    Detects and closes the multi-step tutorial popup on keybr.com.
    It clicks "Next" buttons until it finds and clicks "Close".
    """
    try:
        # Wait a short time for popup to appear
        await page.wait_for_selector("text=Next", timeout=3000)
        print("💬 Tutorial popup detected. Navigating...")

        while True:
            try:
                # Try clicking "Next"
                await page.click("text=Next", timeout=1000)
                print("➡️ Clicked 'Next'")
                await page.wait_for_timeout(300)  # short pause between clicks
            except PlaywrightTimeoutError:
                # If "Next" not found, maybe we reached the final step
                try:
                    await page.click("text=Close", timeout=1000)
                    print("🧹 Closed tutorial popup.")
                    break
                except PlaywrightTimeoutError:
                    print("⚠️ No 'Next' or 'Close' found — exiting loop.")
                    break

    except PlaywrightTimeoutError:
        print("✅ No tutorial popup detected.")

async def getTypingPause():
    return random.uniform(30, 300)

async def typeText(locator, page):
    text_content = await locator.inner_text()
    text_content = text_content.replace("", " ")
    print("\n--- Text to type ---")
    print(text_content)
    print("--------------------")

    count: int = 0
    wasFalse: bool = False
    for char in text_content:
        isFalsePress: bool = random.random() < 0.1  # change false probability
        if isFalsePress and char != ' ':
            charCandidate = await getFalseKey(char)
            if count != 0 or count == len(text_content) - 1:
                if charCandidate != text_content[count - 1]:
                    if text_content[count - 1] == ' ':
                        if not wasFalse:
                            char = charCandidate
                            print(char)
                            wasFalse = True
                        else:
                            wasFalse = False
        await page.keyboard.type(char, delay=await getTypingPause())
        count += 1



async def getFalseKey(char):
    possibleFalseKeys = surroundingKeysMap[char]
    return random.choice(possibleFalseKeys)


async def main(trainingTime, attempts):
    # List of common ad and tracking domains to block
    blocked_domains = [
        "googlesyndication.com",
        "google-analytics.com",
        "doubleclick.net",
        "adservice.google.com",
        "googletagservices.com",
        "c.amazon-adsystem.com",
        "ads.pubmatic.com",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1200, "height": 800},
            user_agent=random_user_agent()
        )

        # Block ad domains
        await context.route(
            lambda url: urlparse(url).hostname and any(domain in urlparse(url).hostname for domain in blocked_domains),
            lambda route: route.abort()
        )

        page = await context.new_page()

        # 1️⃣ Go to keybr.com
        await page.goto("https://www.keybr.com/", wait_until="networkidle")

        await close_tutorial_popup(page)

        #await login(page)

        # 2️⃣ Wait until the typing area loads
        await page.wait_for_selector("main > section")

        # 3️⃣ Define your structural locator
        locator = page.locator(
            "main > section > div:nth-of-type(2) > div > div"
        )

        # 4️⃣ Wait until it exists and is visible
        await locator.wait_for(state="visible")

        # 5️⃣ Click on the element
        await locator.click()
        print("✅ Clicked on the typing area!")

        while attempts > 0 or trainingTime > 0:
            if attempts > 0:
                print("Attempt nr: " + str(attempts))
                await typeText(locator, page)
                attempts -= 1
            elif trainingTime > 0:
                # This part will run after all attempts are used
                await typeText(locator, page)
                trainingTime -= 50 # Assuming typeText takes about 50s

            if attempts <= 0 and trainingTime <= 0:
                break

            await random_pause()

        # 7️⃣ Optional: keep browser open for inspection
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main(trainingTime, attempts))