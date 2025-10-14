import asyncio
from playwright.async_api import async_playwright

mailAdress = "Z125513@shibaura-it.ac.jp"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto('https://www.keybr.com/account')
        await page.click("text=Sign-In")
        await page.get_by_placeholder("Your e-mail address").fill(mailAdress)
        await page.click("text=Send a sign-in link")
        print("A sign-in link has been sent to your email.")

        login_link = input("Please paste the login link from your email here: ")
        await page.goto(login_link)

        print("Login successful. Waiting for navigation...")
        await page.wait_for_url("https://www.keybr.com/account", timeout=60000)

        # Save storage state to a file
        await context.storage_state(path="auth_state.json")
        print("Authentication state saved to 'auth_state.json'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
