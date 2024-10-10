import asyncio
from pyppeteer import launch

async def login_to_solarweb():
    browser = None
    try:
        # Launch the browser
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
        
        # Wait for a specific element or navigation to avoid execution context destruction
        await page.waitForNavigation({'waitUntil': 'domcontentloaded', 'timeout': 90000})  # Increase timeout if necessary
        
        # Step 4: Scrape the earnings data using specific property names
        earnings_data = await page.evaluate('''() => {
            return {
                today: document.querySelector('div[js-earning-today] .js-savings-value')?.innerText || "N/A",
                month: document.querySelector('div[js-earning-month] .js-savings-value')?.innerText || "N/A",
                year: document.querySelector('div[js-earning-year] .js-savings-value')?.innerText || "N/A",
                total: document.querySelector('div[js-earning-total] .js-savings-value')?.innerText || "N/A",
            };
        }''')

        # Print the earnings data
        print("Earnings Data:")
        print(f"Today: {earnings_data['today']} INR")
        print(f"This Month: {earnings_data['month']} INR")
        print(f"This Year: {earnings_data['year']} INR")
        print(f"Total: {earnings_data['total']} INR")

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
