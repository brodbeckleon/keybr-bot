import asyncio
import random
import time

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Config:
mailAdress = "Z125513@shibaura-it.ac.jp"
trainingTime = 0
attempts = 5


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
    random_pause()

    await page.get_by_placeholder("Your e-mail address").fill(mailAdress, timeout=1000)
    print("filled in the mail adress")

    random_pause()
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.click("text=Send a sign-in link", timeout=1000)
    print("Requested a Sign-in link")

    loginLink: str = input("Enter the login link: ")

    await page.goto(loginLink, timeout=1000)

def random_pause():
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
    random_pause = random.uniform(50, 200)
    time.sleep(random_pause)
    return random_pause

async def typeText(locator, page):
    text_content = await locator.inner_text()
    text_content = text_content.replace("", " ")
    print("\n--- Text to type ---")
    print(text_content)
    print("--------------------")
    await page.keyboard.type(text_content, delay=getTypingPause())

async def main(trainingTime, attempts):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False = shows the browser
        page = await browser.new_page()

        # 1️⃣ Go to keybr.com
        await page.goto("https://www.keybr.com/")

        await close_tutorial_popup(page)

        #await login(page)

        # 2️⃣ Wait until the typing area loads
        # (This ensures the DOM structure is ready)
        await page.wait_for_selector("main > section")

        # 3️⃣ Define your structural locator (Option A)
        locator = page.locator(
            "main > section > div:nth-of-type(2) > div > div"
        )

        # 4️⃣ Wait until it exists and is visible
        await locator.wait_for(state="visible")

        # 5️⃣ Click on the element
        await locator.click()
        print("✅ Clicked on the typing area!")

        while True:
            if attempts != 0:
                await typeText(locator, page)
                attempts -= 1

            if trainingTime >= 0:
                await typeText(locator, page)
                await asyncio.sleep(50)
                trainingTime -= 50
            if attempts == 0 & trainingTime == 0: break

    # 7️⃣ Optional: keep browser open for inspection
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main(trainingTime, attempts))