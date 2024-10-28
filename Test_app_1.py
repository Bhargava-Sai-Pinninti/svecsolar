from flask import Flask, jsonify
import threading
from datetime import datetime
import json
import os
import asyncio
from pyppeteer import launch

app = Flask(__name__)

# Store global references to browser and page
browser_1,page_1 = None,None


async def login_1():
        print("working in login_2() ---- 2.2 \n")
        global browser_1, page_1
        json_file_path = 'website1_credentials.json'
        with open(json_file_path, 'r') as json_file:
            creds = json.load(json_file)
        # Launch browser in headless mode
        browser_1 = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        page_1 = await browser_1.newPage()

        # Step 1: Navigate to login page
        await page_1.goto("https://server.growatt.com/login", {'waitUntil': 'networkidle2','timeout': 190000})
        await asyncio.sleep(1)
        # Step 2: Fill in login details
        await page_1.type('#val_loginAccount', creds['user_id'])
        await page_1.type('#val_loginPwd', creds['password'])


        # Step 3: Click login button and wait for navigation to complete
        await page_1.click('.loginB')
        await page_1.waitForNavigation({'waitUntil': 'networkidle2','timeout': 190000})

        # Step 4: Click the "All Devices" button and wait for the page to load
        try:
            await page_1.waitForSelector('.btn_toAllDevices', {'visible': True,'timeout': 190000})
            await page_1.click('.btn_toAllDevices')
            await asyncio.sleep(1)
            # Wait for the device panel to load (increased timeout)
            await page_1.waitForSelector('.devicePageDataPanel', {'visible': True,'timeout': 190000})
            await asyncio.sleep(1)
            print("\n Login successful! --- ")
            return page_1
        except Exception as e:
            print(f"Error during navigation or waiting for device panel: {e}")
            return None
        

async def scrape_data_1():
    print("working in data scrape_data()... ---- 2\n")
    global page_1  # Use the global page object
    if not page_1:
        print("issue in getting page so relogin... ---- 2.1\n")
        page_1=await login_1()
        print("working in data scrape_data() after relog done... 3 \n")
    else:
        print("page3 get from global... 3\n")
        # Step 6: Scrape plant data
        # Step 5: Extract data from the tables
    try:
        await asyncio.sleep(3)
        power_data = await page_1.evaluate('''() => {
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
        return power_data
    except Exception as e:
            print(f"Error extracting data in 1: {e}")


async def update_data():
    """Periodically update data and store it in a JSON file."""
    json_file_path = 'data.json'
    alert = ""

    # Load existing data
    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                stored_data = json.load(json_file)
        else:
            stored_data = {"website_1": None, "last_time_website_1": None}
    except:
        stored_data = {"website_1": None, "last_time_website_1": None}

    try:
        # Scrape data
        data_website_1 = await scrape_data_1()
        # Update data in storage
        stored_data['website_1'] = data_website_1
        stored_data['last_time_website_1'] = datetime.now().strftime('%Y-%m-%d / %H:%M')
    except Exception as e:
        alert += f"\nError fetching data: {e}"

    stored_data["alert_data"] = alert

    # Save updated data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(stored_data, json_file)
    print("\n stored data ----- 4",stored_data)



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

