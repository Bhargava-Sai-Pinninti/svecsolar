import asyncio
from pyppeteer import launch

async def scrape_website():
    # Launch browser in headless mode
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Step 1: Navigate to login page
    await page.goto("https://server.growatt.com/login")

    # Step 2: Fill in login details
    await page.type('#val_loginAccount', 'sri vasavi educational society')
    await page.type('#val_loginPwd', 'Solar30')

    # Step 3: Click login button and wait for navigation to complete
    await page.click('.loginB')
    await page.waitForNavigation()

    # Step 4: Wait for the page to load
    await asyncio.sleep(5)  # Wait for 5 seconds to allow elements and scripts to load

    # Step 5: Click the "All Devices" button to trigger the toAllPlant() function
    try:
        await page.click('.btn_toAllDevices')  # Click the button instead of calling the JS function directly
    except Exception as e:
        print(f"Error: {e}")
        await browser.close()
        return

    # Step 6: Wait for the data panel to appear after clicking the button
    await page.waitForSelector('.devicePageDataPanel')  # Wait for data panel to load
    await asyncio.sleep(5)  # Wait for 5 seconds to allow elements and scripts to load
    # Step 7: Extract required data
    power_data = await page.evaluate('''() => {
        return {
            currentPower: document.querySelector('.val_device_plantPac').innerText,
            ratedPower: document.querySelector('.val_device_plantNominalPower').innerText,
            generationToday: document.querySelector('.val_device_plantEToday').innerText,
            generationTotal: document.querySelector('.val_device_plantETotal').innerText,
            revenueToday: document.querySelector('.val_device_plantMToday').innerText,
            revenueTotal: document.querySelector('.val_device_plantMTotal').innerText
        }
    }''')

    # Step 8: Print the extracted data
    print(f"Current Power: {power_data['currentPower']} kW")
    print(f"Rated Power: {power_data['ratedPower']} kW")
    print(f"Generation Today: {power_data['generationToday']} kWh")
    print(f"Total Generation: {power_data['generationTotal']} kWh")
    print(f"Revenue Today: ₹{power_data['revenueToday']}")
    print(f"Total Revenue: ₹{power_data['revenueTotal']}")

    # Step 9: Close the browser
    await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_website())

