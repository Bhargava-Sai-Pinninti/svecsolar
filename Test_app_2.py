from flask import Flask, jsonify
import threading
from datetime import datetime
import json
import os
import asyncio
from pyppeteer import launch

app = Flask(__name__)

# Store global references to browser and page
browser_2,page_2 = None,None

async def login_2():
    print("working in login_2() ---- 2.2 \n")
    global browser_2, page_2

    if not browser_2 or not page_2:  # If the browser or page is not available, create them
        json_file_path = 'website2_credentials.json'
        with open(json_file_path, 'r') as json_file:
            creds = json.load(json_file)
        # Launch the browser
        browser_2 = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        page_2 = await browser_2.newPage()

        # Navigate to login page and perform login
        await page_2.goto("https://www.solarweb.com/Account/ExternalLogin", {'waitUntil': 'networkidle2', 'timeout': 90000})
        await asyncio.sleep(1)

        # Fill in login credentials
        await page_2.type('input[name="usernameUserInput"]', creds['user_id'], {'delay': 100})
        await page_2.type('input[name="password"]', creds['password'], {'delay': 100})
        await asyncio.sleep(2)

        # Click login button
        await page_2.waitForSelector('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn', {'visible': True})
        await page_2.click('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn')

        # Wait for login to complete
        await page_2.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 90000})
        print("Logged in successfully \n")

    return page_2  # Return the page object


async def scrape_data_2():
    print("working in data scrape_data()... ---- 2\n")
    """Scrape data using the existing page object."""
    global page_2  # Use the global page object
    if not page_2:
        print("issue in getting page so relogin... ---- 2.1\n")
        page_2=await login_2()
        print("working in data scrape_data() after relog done... 3\n")
    else:
        print("page2 get from global... 3\n")

    # Wait for the data container to load
    await page_2.waitForSelector('div[data-swiper-slide-index="0"]', {'timeout': 30000})
    await asyncio.sleep(2)

    # Extract the required data
    power_data = await page_2.evaluate('''() => {
        const ETodayDiv = document.querySelector('div[data-swiper-slide-index="0"]');
        const EMonthDiv = document.querySelector('div[data-swiper-slide-index="1"]');
        const EYearDiv = document.querySelector('div[data-swiper-slide-index="2"]');
        const ETotalDiv = document.querySelector('div[data-swiper-slide-index="3"]');

        const CurrentPower = document.querySelector('.js-status-bar-text')?.innerText || "N/A";
        const EnergyBalanceToday = document.querySelector('.text-to-grid.js-production')?.innerText || "N/A";

        const EToday = ETodayDiv ? `${ETodayDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETodayDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
        const EMonth = EMonthDiv ? `${EMonthDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EMonthDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
        const EYear = EYearDiv ? `${EYearDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EYearDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
        const ETotal = ETotalDiv ? `${ETotalDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETotalDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";

        return { CurrentPower, EnergyBalanceToday, EToday, EMonth, EYear, ETotal };
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
        stored_data = {"website_2": None, "last_time_website_2": None}

    try:
        # Scrape data
        data_website_2 = await scrape_data_2()
        # Update data in storage
        stored_data['website_2'] = data_website_2
        stored_data['last_time_website_2'] = datetime.now().strftime('%Y-%m-%d / %H:%M')
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

