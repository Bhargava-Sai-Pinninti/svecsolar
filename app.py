from flask import Flask, request, render_template
import threading
from datetime import datetime, time 
import json
import os
import asyncio
from pyppeteer import launch

app = Flask(__name__)

# Store global references to browser and page
browser_1,page_1 = None,None
# Store global references to browser and page
browser_2,page_2 = None,None
# Global variables to store browser and page objects for each website
browser_3, page_3 = None, None

async def login_1():
        try:
            print("<<S1>> working in login_1() ---- 2.2 \n")
            global browser_1, page_1
            json_file_path = 'website1_credentials.json'
            with open(json_file_path, 'r') as json_file:
                creds = json.load(json_file)
            # Launch browser in headless mode
            browser_1 = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
            page_1 = await browser_1.newPage()

            # Step 1: Navigate to login page
            await page_1.goto("https://server.growatt.com/login", {'waitUntil': 'networkidle2','timeout': 99999})
            await asyncio.sleep(1)
            # Step 2: Fill in login details
            await page_1.type('#val_loginAccount', creds['user_id'])
            await page_1.type('#val_loginPwd', creds['password'])


            # Step 3: Click login button and wait for navigation to complete
            await page_1.click('.loginB')
            await page_1.waitForNavigation({'waitUntil': 'networkidle2','timeout': 99999})

            # Step 4: Click the "All Devices" button and wait for the page to load
            
            await page_1.waitForSelector('.btn_toAllDevices', {'visible': True,'timeout': 99999})
            await page_1.click('.btn_toAllDevices')
            await asyncio.sleep(1)
            # Wait for the device panel to load (increased timeout)
            await page_1.waitForSelector('.devicePageDataPanel', {'visible': True,'timeout': 99999})
            await asyncio.sleep(1)
            print("\n<<s1>> Login successful! in 1 --- 3")
            return page_1
        except Exception as e:
            if browser_1:
                await browser_1.close()
            browser_1,page_1 = None,None
            print(f"<<S1>> Error in S1 : {e}")
            return e
        
async def scrape_data_1():
    try:
        print("<<s1>> working in data scrape_data()... ---- 2\n")
        global browser_1,page_1  # Use the global page object
        if not page_1:
            print("<<s1>> issue in getting page so relogin... ---- 2.1\n")
            page_1=await login_1()
            print("<<s1>> working in data scrape_data() after relog done... 3 \n")
        else:
            print("page1 get from global... 3\n")
            # Step 6: Scrape plant data
            # Step 5: Extract data from the tables
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
        print("<<s1>> yes data getted sucessfully \n")
        return power_data
    except Exception as e:
            if browser_1:
                await browser_1.close()
            browser_1,page_1 = None,None
            print(f"Error extracting data in 1: {e}")
            return e
  
async def login_2():
    try:
        print("<S2> working in login_2() ---- 2.2 \n")
        global browser_2, page_2
        if not browser_2 or not page_2:  # If the browser or page is not available, create them
            json_file_path = 'website2_credentials.json'
            with open(json_file_path, 'r') as json_file:
                creds = json.load(json_file)
            # Launch the browser
            browser_2 = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
            page_2 = await browser_2.newPage()

            # Navigate to login page and perform login
            await page_2.goto("https://www.solarweb.com/Account/ExternalLogin", {'waitUntil': 'networkidle2', 'timeout': 99999})
            await asyncio.sleep(2)

            # Fill in login credentials
            await page_2.type('input[name="usernameUserInput"]', creds['user_id'], {'delay': 150})
            await page_2.type('input[name="password"]', creds['password'], {'delay': 150})
            await asyncio.sleep(1)

            # Click login button
            await page_2.waitForSelector('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn', {'visible': True})
            await page_2.click('.btn-fro.btn-fro-primary.btn-fro-medium.margin-top-light.keypress-btn')

            # Wait for login to complete
            await page_2.waitForNavigation({'waitUntil': 'networkidle2', 'timeout': 99999})
            print("<S2> Logged in successfully in S2 ----\n")
        
        return page_2  # Return the page object
    except Exception as e:
        if browser_2:
                await browser_2.close()
        browser_2,page_2 = None,None
        print(f" <S2> Error in login 2(){e} \n")
        return e

async def scrape_data_2():
    try:
        print("<<S2>> working in data scrape_data_2()... ---- 2\n")
        """Scrape data using the existing page object."""
        global browser_2,page_2  # Use the global page object
        if not page_2:
            print("<<S2>> issue in getting page so relogin in S2 login ---- 2.1\n")
            page_2=await login_2()
            print("<<S2>> working in data scrape_data_2() after relog done... 3\n")
        else:
            print("<<S2>> page2 get from global... 3\n")

        # Wait for the data container to load
        await page_2.waitForSelector('div[data-swiper-slide-index="0"]', {'timeout': 99999})
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
            print("\n <<S2>> yes done data getted \n")
        return power_data
    
    except Exception as e:
        if browser_2:
            await browser_2.close()
        browser_2,page_2 = None,None
        print(f"Error in  Scrape_data_2(){e} \n")
        return e

async def login_3():
    try:
        print("<S3> working in login_3() ---- 2.2 \n")
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
                await page_3.goto("https://web3.isolarcloud.com.hk/#/login", {'waitUntil': 'networkidle2', 'timeout': 99999})

                # Allow some time for rendering
                await asyncio.sleep(2)

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
                await page_3.type(f'#{inputs["accountId"]}', creds['user_id'], {'delay': 120})
                await page_3.type(f'#{inputs["passwordId"]}', creds['password'], {'delay': 120})

                # Step 4: Click the login button
                login_button = await page_3.evaluateHandle('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    return buttons.find(button => button.textContent.trim() === 'Login');
                }''')

                if login_button:
                    await login_button.click()
                    
                else:
                    raise Exception("<S3> Login button not found. in 3 \n")

                # Step 5: Wait for the plant data table to load
                await page_3.waitForSelector('.plant-name-column', {'timeout': 99999})
                print("\n <S3> Login successful! in S3 --- \n")
                await asyncio.sleep(2)
                return page_3
            except Exception as e:
                if browser_3:
                    await browser_3.close()
                browser_3,page_3 = None,None
                print(f"<S3> Error during scraping in login_3(): {e} \n")
                return e
        return page_3  # Return the page object
    except Exception as e:
                if browser_3:
                    await browser_3.close()
                browser_3,page_3 = None,None
                print(f"<S3> Error during scraping in  login_3(): {e} \n")
                return e

async def scrape_data_3():
    try:
        print("<<S3>> working in data scrape_data_3()... ---- 2\n")
        """Scrape data using the existing page object."""
        global browser_3,page_3  # Use the global page object
        if not page_3:
            print("<<S3>> issue in getting page so relogin in S3... ---- 2.1\n")
            page_3=await login_3()
            print("<<S3>> working in data scrape_data() after relog done in S3... 3 \n")
        else:
            print("<<S3>> page3 get from global... 3\n")
            # Step 6: Scrape plant data
        await asyncio.sleep(2)
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
            print("<<S3>> yes done data getted ---- \n")
        return power_data
    except Exception as e:
        if browser_3:
                await browser_3.close()
        browser_3,page_3 = None,None
        print(f" <<S3>> Error in Scrape_data_3(): {e} \n")
        return e

async def update_data():
    global browser_1,page_1,browser_2,page_2,browser_3,page_3
    try:
        with app.app_context():  # Push the app context
            json_file_path = 'data.json'
            alert = ""
            alert_1=""
            alert_2=""
            alert_3=""
            data_website_1, data_website_2 , data_website_3 = None, None ,None

            # Load existing data
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as json_file:
                    stored_data = json.load(json_file)
            else:
                stored_data = {"website_1": None, "website_2": None, "website_3": None, "last_time_website_1": None, "last_time_website_2": None , "last_time_website_3": None}

            # Run both scraping functions concurrently
            try:
                data_website_1, data_website_2, data_website_3 = await asyncio.gather(
                scrape_data_1(),
                scrape_data_2(),
                scrape_data_3(),
                return_exceptions=True  
            )

                # Handle scraping results
                if isinstance(data_website_1, Exception):
                    alert_1 += "Growatt Not Updated !!"
                else:
                    stored_data['website_1'] = data_website_1
                    stored_data['last_time_website_1'] = datetime.now().strftime('%Y-%m-%d / %H:%M')

                if isinstance(data_website_2, Exception):
                    alert_2 += "Fronius Not Updated !!"
                else:
                    stored_data['website_2'] = data_website_2
                    stored_data['last_time_website_2'] = datetime.now().strftime('%Y-%m-%d / %H:%M')

                if isinstance(data_website_3, Exception):  # If website 3 raised an exception
                    alert_3 += "iSolar Cloud Not Updated !!"
                else:  # If website 3 was successful
                    stored_data['website_3'] = data_website_3[0]
                    stored_data['last_time_website_3'] = datetime.now().strftime('%Y-%m-%d / %H:%M')

            except Exception as e:
                alert += f"Error fetching data: {e} ! \n"

            stored_data["alert_data"],stored_data["alert_data1"],stored_data["alert_data2"],stored_data["alert_data3"]  = alert,alert_1,alert_2,alert_3

            # Save the updated data to JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(stored_data, json_file)

            print(data_website_1,"\n")
            print(data_website_2,"\n")
            print(data_website_3,"\n")

    except Exception as e:
        print(f"Error in update(): {e} \n")
        return e
    
    try:
        if page_1:
            print("refreshing p1 \n")
            await page_1.reload({'waitUntil': 'networkidle2', 'timeout': 99999})
            print("refreshing done p1 \n")
        if page_2:
            print("refreshing p2 \n")
            await page_2.reload({'waitUntil': 'networkidle2', 'timeout': 99999})
            print("refreshing done p2 \n")
        if page_3:
            print("refreshing p3 \n")
            await page_3.reload({'waitUntil': 'networkidle2', 'timeout': 99999})
            print("refreshing done p3 \n")
    except Exception as e:
        print(f"Error in refresh : {e} \n")
        return e

async def run_updates():
    """Run updates periodically in a loop with different intervals based on time."""
    while True:
        try:
            now = datetime.now().time()
            if now: # Between 5 AM and 7 PM time(5, 0) <= now < time(19, 0): 
                print("\n started in run_updates()  ---- 1")
                await update_data()
                await asyncio.sleep(90)  # 90 seconds interval
                print("\n ended in run_updates() ---- end")
            else:  # Between 7 PM and 5 AM
                print("\n Out of active hours. Sleeping for 30 minutes.")
                await asyncio.sleep(7200)  # 240 minutes interval
        except Exception as e:
            print(f"Exception in run_updates: {e}")
            await asyncio.sleep(5)  # Retry after 5 seconds
            await update_data()

def start_background_task():
    """Start the background update task in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_updates())

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

# Route to update website 3 credentials
@app.route('/update_website3', methods=['POST'])
def update_website3():
    try:
        user_id = request.form['user_id3']
        password = request.form['password3']
        
        # Data to be saved
        data = {
            "user_id": user_id,
            "password": password
        }
        
        # File path for Website 3 credentials
        file_path = 'website3_credentials.json'
        
        # Save the credentials to the file
        save_credentials(file_path, data)
        
        return render_template('success.html')
    except Exception as e:
        print(f"Error extracting data: {e}")
        return render_template('error.html')
    
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    # Start the background task thread
    threading.Thread(target=start_background_task, daemon=True).start()
    app.run(host="0.0.0.0", port=8080,debug=True, use_reloader=False)
