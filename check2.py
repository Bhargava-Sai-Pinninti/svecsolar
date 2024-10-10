from flask import Flask, request, render_template, jsonify
from datetime import datetime
import json
import os
import asyncio
from pyppeteer import launch
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
        print(power_data) 

if __name__ == "__main__":
    asyncio.run(scrape_website_2())
    print("Program End")

