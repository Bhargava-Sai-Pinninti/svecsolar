import asyncio
from pyppeteer import launch

async def scrape_website_1():
    # Launch headless browser
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Go to the login page
    await page.goto("https://server.growatt.com/login")

    # Fill in login details
    await page.type('#val_loginAccount', 'sri vasavi educational society')
    await page.type('#val_loginPwd', 'Solar30')

    # Click login button
    await page.click('.loginB')

    # Wait for navigation to complete after login
    await page.waitForNavigation()

    # Go to the page with the data
    await page.goto("https://server.growatt.com/index")

    # Wait for the data elements to load
    await page.waitForSelector('.val_eToday', timeout=20000)  # 20 second timeout

    # Extra delay to ensure the page is fully loaded
    await page.waitFor(6000)  # Wait for 5 more seconds

    # Extract the data
    eToday = await page.evaluate("document.querySelector('.val_eToday').innerText")
    eTotal = await page.evaluate("document.querySelector('.val_eTotal').innerText")
    mToday = await page.evaluate("document.querySelector('.val_mToday').innerText")
    mTotal = await page.evaluate("document.querySelector('.val_mTotal').innerText")

    # Close the browser
    await browser.close()

    # Return the scraped data
    return {
        "eToday": eToday,
        "eTotal": eTotal,
        "mToday": mToday,
        "mTotal": mTotal
    }

# Run the scraping function
if __name__ == "__main__":
    data = asyncio.get_event_loop().run_until_complete(scrape_website_1())
    if data:
        print("\nExtracted Data:\n", data)
