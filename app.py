from flask import Flask, request, render_template, jsonify
from datetime import datetime
import json
import os
import asyncio
from pyppeteer import launch

app = Flask(__name__)

async def scrape_website_1():
        json_file_path = 'website1_credentials.json'
        with open(json_file_path, 'r') as json_file:
            creds = json.load(json_file)
        # Launch browser in headless mode
        browser = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        page = await browser.newPage()

        # Step 1: Navigate to login page
        await page.goto("https://server.growatt.com/login", {'waitUntil': 'networkidle2','timeout': 190000})
        await asyncio.sleep(1)
        # Step 2: Fill in login details
        await page.type('#val_loginAccount', creds['user_id'])
        await page.type('#val_loginPwd', creds['password'])


        # Step 3: Click login button and wait for navigation to complete
        await page.click('.loginB')
        await page.waitForNavigation({'waitUntil': 'networkidle2','timeout': 190000})

        # Step 4: Click the "All Devices" button and wait for the page to load
        try:
            await page.waitForSelector('.btn_toAllDevices', {'visible': True,'timeout': 190000})
            await page.click('.btn_toAllDevices')
            await asyncio.sleep(1)
            # Wait for the device panel to load (increased timeout)
            await page.waitForSelector('.devicePageDataPanel', {'visible': True,'timeout': 190000})
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error during navigation or waiting for device panel: {e}")
            await browser.close()
            return

        # Step 5: Extract data from the tables
        try:
            await asyncio.sleep(3)
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
            return power_data
        except Exception as e:
            print(f"Error extracting data in 1: {e}")

        finally:
            # Ensure the browser is closed
            if browser is not None:
                await browser.close()
        

async def scrape_website_2():
    
        browser = None
        json_file_path = 'website2_credentials.json'
        with open(json_file_path, 'r') as json_file:
            creds = json.load(json_file)
        # Launch the browser in headless mode
        browser = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        page = await browser.newPage()

        # Step 1: Navigate to the login page
        await page.goto("https://www.solarweb.com/Account/ExternalLogin", {'waitUntil': 'networkidle2','timeout': 90000})
        await asyncio.sleep(1)
        # Step 2: Fill in the login form
        await page.type('input[name="usernameUserInput"]', creds['user_id'], {'delay': 100})  # Enter email
        await page.type('input[name="password"]', creds['password'], {'delay': 100})  # Enter password
        
        # Optional: Wait for a moment before clicking the button
        await asyncio.sleep(2)

        # Step 3: Click the login button using the class name
        await page.waitForSelector('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn', {'visible': True})
        await page.click('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn')  # Click the login button
        
        # Step 4: Wait for navigation to complete after login
        await page.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 190000})  # Increase timeout if necessary
        await asyncio.sleep(5)

        # Step 5: Wait for the specific div containing CO2 savings to appear
        await page.waitForSelector('div[data-swiper-slide-index="0"]', {'timeout': 190000})  # Wait for up to 30 seconds for the div to appear
        await asyncio.sleep(5)
        # Step 6: Retry mechanism to ensure data is loaded
        max_retries = 6
        for attempt in range(max_retries):

            power_data = await page.evaluate('''() => {
    const ETodayDiv = document.querySelector('div[data-swiper-slide-index="0"]');
    const EMonthDiv = document.querySelector('div[data-swiper-slide-index="1"]');
    const EYearDiv = document.querySelector('div[data-swiper-slide-index="2"]');
    const ETotalDiv = document.querySelector('div[data-swiper-slide-index="3"]');

    const CurrentPower = document.querySelector('.js-status-bar-text')?.innerText || "N/A";
    const EnergyBalanceToday = document.querySelector('.text-to-grid.js-production')?.innerText || "N/A";  // Fixed the selector

    const EToday = ETodayDiv ? `${ETodayDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETodayDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
    const EMonth = EMonthDiv ? `${EMonthDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EMonthDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
    const EYear = EYearDiv ? `${EYearDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${EYearDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";
    const ETotal = ETotalDiv ? `${ETotalDiv.querySelector('.savings-value.js-savings-value')?.innerText || "N/A"} ${ETotalDiv.querySelector('.savings-unit.js-savings-unit')?.innerText || ""}` : "N/A";

    return {CurrentPower, EnergyBalanceToday, EToday, EMonth, EYear, ETotal };
}''')

            # If the data is still not loaded, wait a bit longer and retry
            if power_data and all(value != "N/A" for value in power_data.values()):
                break  # If data is available, stop retrying
            await asyncio.sleep(1)  # Wait before the next retry
        if browser is not None:
                await browser.close()
        return power_data


# Flask route to display the combined data
@app.route('/')
@app.route('/home')
def index():
    try:
        json_file_path = 'data.json'
            # Read the data from data.json and pass it to the template
        with open(json_file_path, 'r') as json_file:
            stored_data = json.load(json_file)
        # Render the results on the index.html page

        return render_template('home.html', data=stored_data)
    except Exception as e:
        print(f"Error extracting data: {e}")
        return str(e)


# Flask route to display the combined data
@app.route('/updatedata')
async def updatedata():
    json_file_path = 'data.json'
    alert = ""
    data_website_1 = None
    data_website_2 = None

    # Load existing data to preserve in case one website fails
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            stored_data = json.load(json_file)
    else:
        stored_data = {"website_1": None, "website_2": None, "last_time_website_1": None, "last_time_website_2": None}

    # Run both scraping functions concurrently, but handle their success/failure independently
    try:
        data_website_1 = await scrape_website_1()
        data_website_2 = await scrape_website_2()
        # Handle the result of website 1 (Growatt)
        if isinstance(data_website_1, Exception):  # If website 1 raised an exception
            alert += "\n Issue in fetching Growatt data. \n"
        else:  # If website 1 was successful
            stored_data['website_1'] = data_website_1
            stored_data['last_time_website_1'] = datetime.now().strftime('%Y-%m-%d / %H:%M')

        # Handle the result of website 2 (Fronius)
        if isinstance(data_website_2, Exception):  # If website 2 raised an exception
            alert += "\n Issue fetching Fronius data. \n"
        else:  # If website 2 was successful
            stored_data['website_2'] = data_website_2
            stored_data['last_time_website_2'] = datetime.now().strftime('%Y-%m-%d / %H:%M')

    except Exception as e:
        alert += f"\nError fetching data: {e}"

    # Add alert messages and save the combined data
    stored_data["alert_data"] = alert

    # Save the updated data to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(stored_data, json_file)

    return jsonify({"status": "done"})


# Route for rendering the update page
@app.route('/updatep', methods=['GET'])
def updateP():
    try:
        return render_template('update.html')
    except Exception as e:
        print(f"Error extracting data: {e}")

# Function to clear or create JSON file
def save_credentials(file_path, data):
    try:
        # Check if file exists, create it if not
        if not os.path.exists(file_path):
            with open(file_path, 'w') as json_file:
                json.dump({}, json_file)  # Creating an empty JSON file

        # Open file and write the new data (clearing the old data)
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        print(f"Error extracting data: {e}")

# Route to update website 1 credentials
@app.route('/update_website1', methods=['POST'])
def update_website1():
    try:
        user_id = request.form['user_id1']
        password = request.form['password1']
        
        # Data to be saved
        data = {
            "user_id": user_id,
            "password": password
        }
        
        # File path for Website 1 credentials
        file_path = 'website1_credentials.json'
        
        # Save the credentials to the file
        save_credentials(file_path, data)
        
        return render_template('success.html')
    except Exception as e:   
        print(f"Error extracting data: {e}")
        return render_template('error.html')

# Route to update website 2 credentials
@app.route('/update_website2', methods=['POST'])
def update_website2():
    try:
        user_id = request.form['user_id2']
        password = request.form['password2']
        
        # Data to be saved
        data = {
            "user_id": user_id,
            "password": password
        }
        
        # File path for Website 2 credentials
        file_path = 'website2_credentials.json'
        
        # Save the credentials to the file
        save_credentials(file_path, data)
        
        return render_template('success.html')
    except Exception as e:
        print(f"Error extracting data: {e}")
        return render_template('error.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
