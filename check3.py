import asyncio
from pyppeteer import launch
import json

async def scrape_website_3():
    # Load credentials from the JSON file
    json_file_path = 'website3_credentials.json'
    with open(json_file_path, 'r') as json_file:
        creds = json.load(json_file)

    # Launch the browser
    browser = await launch(headless=True)  # Set headless=True for production
    page = await browser.newPage()

    try:
        # Step 1: Navigate to the login page
        await page.goto("https://web3.isolarcloud.com.hk/#/login", 
                        {'waitUntil': 'networkidle2', 'timeout': 190000})
        print("Page loaded successfully")

        # Allow some time for rendering
        await asyncio.sleep(3)

        # Step 2: Extract input field IDs dynamically
        inputs = await page.evaluate('''() => {
            const accountInput = document.querySelector('input[placeholder="Account"]');
            const passwordInput = document.querySelector('input[placeholder="Password"]');
            return {
                accountId: accountInput ? accountInput.id : null,
                passwordId: passwordInput ? passwordInput.id : null
            };
        }''')

        if not inputs['accountId'] or not inputs['passwordId']:
            raise Exception("Input fields not found.")

        print(f"Found dynamic IDs: Account ID = {inputs['accountId']}, Password ID = {inputs['passwordId']}")

        # Step 3: Enter credentials
        await page.type(f'#{inputs["accountId"]}', creds['user_id'], {'delay': 100})
        await page.type(f'#{inputs["passwordId"]}', creds['password'], {'delay': 100})

        # Step 4: Click the login button
        login_button = await page.evaluateHandle('''() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(button => button.textContent.trim() === 'Login');
        }''')

        if login_button:
            await login_button.click()
            print("Clicked the login button.")
        else:
            raise Exception("Login button not found.")

        # Step 5: Wait for the plant data table to load
        await page.waitForSelector('.plant-name-column', {'timeout': 90000})
        print("Login successful!")
        await asyncio.sleep(3)

        # Step 6: Scrape plant data
        plant_data = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('tr.el-table__row'));
            return rows.map(row => {
                const columns = row.querySelectorAll('td');
                return {
                    plant_name: columns[0]?.innerText.trim() || '',
                    location: columns[1]?.innerText.trim() || '',
                    status: columns[2]?.innerText.trim() || '',
                    capacity: columns[3]?.innerText.trim() || '',
                    power: columns[4]?.innerText.trim() || '',
                    daily_energy: columns[5]?.innerText.trim() || '',
                    monthly_energy: columns[6]?.innerText.trim() || '',
                    yearly_energy: columns[7]?.innerText.trim() || '',
                    total_energy: columns[8]?.innerText.trim() || '',
                    operation_hours: columns[9]?.innerText.trim() || ''
                };
            });
        }''')

        print("Scraped Plant Data:",plant_data)
        return plant_data

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_website_3())
