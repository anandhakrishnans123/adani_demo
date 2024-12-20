import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import time
if st.button("Upload file to the system"):
# Streamlit output
    st.write("Starting the test…")

    # Define the login and file upload function
    async def main():
        async with async_playwright() as p:
            # Launch the browser with visibility
            browser = await p.chromium.launch(headless=True)  # This will open the browser so you can see what's happening
            page = await browser.new_page()
            
            # Clear cookies before starting
            await page.context.clear_cookies()
            
            # Navigate to the website login page
            await page.goto('https://samesg.samcorporate.com/auth/login')
            
            # Wait for the "Login" button and click it
            await page.wait_for_selector('text=Login', timeout=60000)
            await page.click('text=Login')
            
            # Wait for the login page to load completely
            await page.wait_for_url('**/login', timeout=60000)
            
            # Fill in the login credentials (replace with actual values)
            email = "rinasusman@samcorporate.com"  # Replace with actual email
            password = "987654321"  # Replace with actual password
            
            # Fill in the email and password fields
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', password)
            
            # Click the submit button to log in
            await page.click('button[type="submit"]')
            
            # Wait for the page to load after login
            await page.wait_for_load_state('load', timeout=60000)  # Wait for the page to finish loading
            await asyncio.sleep(20)
            
            # Navigate to the target page after logging in
            target_url = 'https://samesg.samcorporate.com/app/oecs1clayjeh02r4azwfozndif0/page/default/data-upload/etl/emission-calculations/66545e850b4e5b2af3c80e81/list/create'
            await page.goto(target_url)
            
            # Wait for the target page to load completely
            await page.wait_for_load_state('load', timeout=60000)
            await page.wait_for_selector('text=Upload Scope File', timeout=30000)
            await page.click('text=Upload Scope File')
            
            # Select the month and year for the file upload
            await page.wait_for_selector('select#fileMonth', timeout=30000)
            await page.select_option('select#fileMonth', value="4")  # Select March
            await page.wait_for_selector('select#fileYear', timeout=30000)
            await page.select_option('select#fileYear', value="2023")
            file_path = r"C:\Users\DML-LT-36\Desktop\streamlit playwright\Electricity-Sample (12).xlsx"
            file_input_selector = 'input#file[accept=".xlsx, .xls"]'
            await page.wait_for_selector(file_input_selector, timeout=30000)
            file_input = await page.query_selector(file_input_selector)
            if file_input:
                await file_input.set_input_files(file_path)
                print(f"Uploaded file: {file_path}")
            
            await page.click('button:text("Upload File")');

            # Click the upload button
            
            
            # Wait for a moment before taking a screenshot
            await asyncio.sleep(4)
            
            # Take a screenshot after uploading the file
            screenshot_path = "upload_screenshot.png"
            await page.screenshot(path=screenshot_path)  # Save the screenshot as an image file
            
            # Optionally, display the screenshot in Streamlit
            st.image(screenshot_path)

            # Optionally, check if the target page loaded successfully by checking the title or specific element
            title = await page.title()
            st.write(title)
            
            # Wait before closing the browser
            await asyncio.sleep(5)  # Wait for 5 seconds before closing the browser
            
            # Close the browser
            await browser.close()
            return title

    # Run the async function
    if __name__ == '__main__':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        title = loop.run_until_complete(main())
        print(title)
