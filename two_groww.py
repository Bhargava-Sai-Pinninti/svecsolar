import asyncio
from pyppeteer import launch

async def scrape_website():
    # Launch browser in headless mode
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Step 1: Navigate to login page
    await page.goto("https://server.growatt.com/login", {'waitUntil': 'networkidle2'})

    # Step 2: Fill in login details
    await page.type('#val_loginAccount', 'sri vasavi educational society')
    await page.type('#val_loginPwd', 'Solar30')

    # Step 3: Click login button and wait for navigation to complete
    await page.click('.loginB')
    await page.waitForNavigation({'waitUntil': 'networkidle2'})

    # Step 4: Click the "All Devices" button and wait for the page to load
    try:
        await page.waitForSelector('.btn_toAllDevices', {'visible': True,'timeout': 60000})
        await page.click('.btn_toAllDevices')
        await asyncio.sleep(1)
        # Wait for the device panel to load (increased timeout)
        await page.waitForSelector('.devicePageDataPanel', {'visible': True,'timeout': 90000})
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Error during navigation or waiting for device panel: {e}")
        await browser.close()
        return

    # Step 5: Extract data from the tables
    try:
        power_data = await page.evaluate('''() => {
            return {
                currentPower: document.querySelector('.val_device_plantPac')?.innerText || "N/A",
                ratedPower: document.querySelector('.val_device_plantNominalPower')?.innerText || "N/A",
                generationToday: document.querySelector('.val_device_plantEToday')?.innerText || "N/A",
                generationThisMonth: document.querySelector('.val_device_plantEMonth')?.innerText || "N/A",
                totalGeneration: document.querySelector('.val_device_plantETotal')?.innerText || "N/A",
                revenueToday: document.querySelector('.val_device_plantMToday')?.innerText || "N/A",
                revenueThisMonth: document.querySelector('.val_device_plantMMonth')?.innerText || "N/A",
                totalRevenue: document.querySelector('.val_device_plantMTotal')?.innerText || "N/A"
            };
        }''')

        # Step 6: Print the extracted data
        print(power_data)

    except Exception as e:
        print(f"Error extracting data: {e}")

    # Step 7: Close the browser
    await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_website())
