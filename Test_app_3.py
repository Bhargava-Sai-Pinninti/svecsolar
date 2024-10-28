from flask import Flask, request, render_template, jsonify
import threading
from datetime import datetime 
import json
import os
import asyncio
from pyppeteer import launch

app = Flask(__name__)

# Global variables to store browser and page objects for each website
browser_3, page_3 = None, None

async def login_3():
    print("working in login_2() ---- 2.2 \n")
    global browser_3, page_3
    # Load credentials from the JSON file
    json_file_path = 'website3_credentials.json'
    with open(json_file_path, 'r') as json_file:
        creds = json.load(json_file)
    if not browser_3 or not page_3:
        browser_3 = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)  # Set headless=True for production
        page_3 = await browser_3.newPage()

        try:
            # Step 1: Navigate to the login page
            await page_3.goto("https://web3.isolarcloud.com.hk/#/login", {'waitUntil': 'networkidle2', 'timeout': 190000})

            # Allow some time for rendering
            await asyncio.sleep(3)

            # Step 2: Extract input field IDs dynamically
            inputs = await page_3.evaluate('''() => {
                const accountInput = document.querySelector('input[placeholder="Account"]');
                const passwordInput = document.querySelector('input[placeholder="Password"]');
                return {
                    accountId: accountInput ? accountInput.id : null,
                    passwordId: passwordInput ? passwordInput.id : null
                };
            }''')

            if not inputs['accountId'] or not inputs['passwordId']:
                raise Exception("Input fields not found.")

            # Step 3: Enter credentials
            await page_3.type(f'#{inputs["accountId"]}', creds['user_id'], {'delay': 100})
            await page_3.type(f'#{inputs["passwordId"]}', creds['password'], {'delay': 100})

            # Step 4: Click the login button
            login_button = await page_3.evaluateHandle('''() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(button => button.textContent.trim() === 'Login');
            }''')

            if login_button:
                await login_button.click()
                
            else:
                raise Exception("Login button not found.")

            # Step 5: Wait for the plant data table to load
            await page_3.waitForSelector('.plant-name-column', {'timeout': 90000})
            print("\n Login successful! --- ")
            await asyncio.sleep(3)
            return page_3
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None
    return page_3  # Return the page object


async def scrape_data_3():
    print("working in data scrape_data()... ---- 2\n")
    """Scrape data using the existing page object."""
    global page_3  # Use the global page object
    if not page_3:
        print("issue in getting page so relogin... ---- 2.1\n")
        page_3=await login_3()
        print("working in data scrape_data() after relog done... 3 \n")
    else:
        print("page3 get from global... 3\n")
        # Step 6: Scrape plant data
    power_data = await page_3.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('tr.el-table__row'));
            return rows.map(row => {
                const columns = row.querySelectorAll('td');
                return {
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

    if power_data:
        print("\n yes done data getted ")
    return power_data



async def update_data():
    """Periodically update data and store it in a JSON file."""
    json_file_path = 'data.json'
    alert = ""

    # Load existing data
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            stored_data = json.load(json_file)
    else:
        stored_data = {"website_3": None, "last_time_website_3": None}
    try:
        # Scrape data
        data_website_3 = await scrape_data_3()
        # Update data in storage
        stored_data['website_3'] = data_website_3
        stored_data['last_time_website_3'] = datetime.now().strftime('%Y-%m-%d / %H:%M')
    except Exception as e:
        alert += f"\nError fetching data: {e}"

    stored_data["alert_data"] = alert

    # Save updated data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(stored_data, json_file)
    print("\n stored data ----- 4 \n",stored_data)




async def run_updates():
    """Run updates periodically in a loop."""
    while True:
        try:
            print("\n started in run_updates()  ---- 1")
            await update_data()
            await asyncio.sleep(5)  # Adjust interval as needed
            print("\n ended in run_updates() ---- end")
        except Exception as e:
            print(f"Exception in run_updates: {e}")
            await asyncio.sleep(5)


def start_background_task():
    """Start the background update task in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_updates())


if __name__ == '__main__':
    # Start the background task thread
    threading.Thread(target=start_background_task, daemon=True).start()
    app.run(debug=True, use_reloader=False)

