import asyncio
from pyppeteer import launch

async def login_to_solarweb():
    browser = None
    try:
        # Launch the browser in headless mode
        browser = await launch(headless=True)  # Set to False to see the browser for debugging
        page = await browser.newPage()

        # Step 1: Navigate to the login page
        await page.goto("https://www.solarweb.com/Account/ExternalLogin", {'waitUntil': 'networkidle2'})

        # Step 2: Fill in the login form
        await page.type('input[name="usernameUserInput"]', 'vec100@argosolar.in', {'delay': 100})  # Enter email
        await page.type('input[name="password"]', 'Vasavi@100', {'delay': 100})  # Enter password
        
        # Optional: Wait for a moment before clicking the button
        await asyncio.sleep(1)

        # Step 3: Click the login button using the class name
        await page.waitForSelector('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn', {'visible': True})
        await page.click('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn')  # Click the login button
        
        # Step 4: Wait for navigation to complete after login
        await page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 90000})  # Increase timeout if necessary
        await asyncio.sleep(5)

        # Step 5: Wait for the specific div containing CO2 savings to appear
        await page.waitForSelector('div[data-swiper-slide-index="0"]', {'timeout': 30000})  # Wait for up to 30 seconds for the div to appear
        await asyncio.sleep(5)
        # Step 6: Retry mechanism to ensure data is loaded
        max_retries = 5
        for attempt in range(max_retries):
            power_data = await page.evaluate('''() => {
                const ETodayDiv = document.querySelector('div[data-swiper-slide-index="0"]');
                const EMonthDiv = document.querySelector('div[data-swiper-slide-index="1"]');
                const EYearDiv = document.querySelector('div[data-swiper-slide-index="2"]');
                const ETotalDiv = document.querySelector('div[data-swiper-slide-index="3"]');

                const EToday = ETodayDiv ? `${ETodayDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETodayDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
                const EMonth = EMonthDiv ? `${EMonthDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EMonthDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
                const EYear = EYearDiv ? `${EYearDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EYearDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
                const ETotal = ETotalDiv ? `${ETotalDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETotalDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";

                return { EToday, EMonth, EYear, ETotal };
            }''')

            # Debugging: Print the raw output before formatting
            print(f"Attempt {attempt+1}: Raw Power Data: {power_data}")

            # If the data is still not loaded, wait a bit longer and retry
            if power_data and all(value != "N/A" for value in power_data.values()):
                break  # If data is available, stop retrying
            await asyncio.sleep(2)  # Wait before the next retry
        
        # Print the scraped earnings data
        print("Earnings Data:")
        print(f"Today: {power_data['EToday']}")
        print(f"This Month: {power_data['EMonth']}")
        print(f"This Year: {power_data['EYear']}")
        print(f"Total: {power_data['ETotal']}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the browser is closed
        if browser is not None:
            await browser.close()

# Run the script
if __name__ == "__main__":
    asyncio.run(login_to_solarweb())
    print("Program End")
