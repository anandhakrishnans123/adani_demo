import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF for PDF handling
import io  # To handle in-memory file stream
from io import StringIO
import pandas as pd
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright
import time
# Set up the Streamlit app title
st.title("PDF or Image to Text Extractor")

# Input for API key
api_key = "AIzaSyBA3sUF2AFbcYwrsuY7zVu38dB-pOA-v9c"  # Replace with your API key

if api_key:
    # Configure the Gemini Pro API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Upload an image or a PDF
    uploaded_file = st.file_uploader("Upload an image or PDF", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        # Debugging: Print the uploaded file type
        st.write(f"Uploaded file type: {uploaded_file.type}")

        file_type = uploaded_file.type
        if file_type in ["image/png", "image/jpg", "image/jpeg"]:
            # Handle image files
            img = Image.open(uploaded_file)
            
            # Initialize session state to track image rotation
            if 'rotation_angle' not in st.session_state:
                st.session_state.rotation_angle = 0
            
            # Button to rotate the image by 90 degrees
            if st.button("Rotate Image 90°"):
                st.session_state.rotation_angle += 90
                st.session_state.rotation_angle %= 360  # Ensure angle stays within 0-359 degrees
            
            # Rotate the image and expand it to ensure full dimensions are kept
            rotated_img = img.rotate(st.session_state.rotation_angle, expand=True)
            st.image(rotated_img, caption='Uploaded Image (Rotated)', use_column_width=True)

            # Generate text from the image
            if st.button("Extract Text from Image"):
                try:
                    # Create a prompt for the model
                    prompt = ("Extract the value of net payable amount, title of the image, name and address of the bill receiver, "
                              "date of billing, due date, and circle name from the image.")
                    response = model.generate_content([prompt, rotated_img])  # Assuming this format works with your API
                    st.write(response.txt)

                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif file_type == "application/pdf":
            # Handle PDF files
            pdf_data = uploaded_file.read()  # Read the uploaded file as bytes
            doc = fitz.open("pdf", pdf_data)  # Open the PDF using the correct format for bytes
            full_text = ""
            
            # Extract text from each page
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                full_text += page.get_text()

            # Generate content from the PDF text
            if st.button("Extract and upload to System"):
                try:
                    # Create a prompt for the model
                    prompt = ("Extract the following details from the document and return them in a clean CSV format: "
                              "id:-Amount containing net payable amount, title, id:-name containing name and address of the bill receiver(only 2 words of company name not human name), date of billing, due date,Total energy consumed in KWH ,"
                              "and circle name. Ensure each field is in a separate column with appropriate headers, and return "
                              "'null' for any missing or unclear data. The CSV should be formatted correctly with commas as delimiters "
                              "and no extra spaces or errors.")
                    response = model.generate_content([prompt, full_text])

                    # Debugging: Inspect raw response
                    csv_result = response.text
                    st.write("Raw Response from API:")
                    st.write(csv_result)
                    
                    # Clean and parse CSV
                    # Strip leading/trailing whitespace
                    csv_result = csv_result.strip()
                    
                    # Check if the result starts with 'csv' and remove any non-CSV content
                    if csv_result.lower().startswith("csv"):
                        # If 'csv' is at the start, remove the first line or prefix before the actual data
                        csv_result = csv_result.split("\n", 1)[-1]  # Remove the first line (metadata/description)
                    
                    # Further clean up: remove any extra text that might appear after CSV content
                    lines = csv_result.split("\n")
                    valid_csv = "\n".join(line for line in lines if ',' in line)  # Only keep lines with commas (CSV rows)
                    
                    # Now, read the cleaned CSV content
                    data_io = StringIO(valid_csv)
                    df = pd.read_csv(data_io)
                    
                    # Save the cleaned DataFrame
                    csv_file_path = 'csv_output.csv'
                    df.to_csv(csv_file_path, index=False)
                    
                    st.success(f"CSV file saved as {csv_file_path}")
                    st.write("Generated DataFrame:")
                    st.write(df)

                    columns = [
                        'Res_Date', 'Department', 'Facility', 'Start Date', 'End Date', 
                        'Country', 'City', 'Activity', 'Activity Unit', 'Energy Type', 
                        'Energy Unit', 'Energy Consumption', 'Cost', 'Price p/u', 'CF Standard', 'Gas'
                    ]

                    # Create an empty DataFrame with the specified columns
                    df2 = pd.DataFrame(columns=columns)
                    # Add values from the original DataFrame
                    df2['Cost'] = df['id:-Amount']
                    df2['End Date'] = df['due date']
                    df2['Start Date'] = df['date of billing']
                    # df2['Facility'] = df['id:-name']
                    df2['City'] = df['circle name']
                    df2['Res_Date'] = datetime.now().strftime('%Y-%m-%d')
                    df2["Energy Unit"] = "KWh"
                    df2['CF Standard'] = "IMO"
                    df2['Gas'] = "CO2"
                    df2['Country'] = "India"
                    df2['Energy Type'] = "India"
                    df2["Energy Consumption"] = df["Total energy consumed in KWH"]
                    df2['End Date'] = pd.to_datetime(df2['End Date'], dayfirst=True)
                    df2['Start Date'] = pd.to_datetime(df2['Start Date'], dayfirst=True)
                    df2['Res_Date'] = pd.to_datetime(df2['Res_Date'], dayfirst=True)
                    
                    # Create an in-memory Excel file
                    excel_buffer = io.BytesIO()
                    df2.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)  # Move the pointer to the start of the buffer
                    excel_file = r'C:\Users\DML-LT-36\Desktop\streamlit playwright\downloaded_data.xlsx'

# Save your Excel file to the specified path
                    with open(excel_file, 'wb') as f:
                        f.write(excel_buffer.getvalue())
#-------------------------------------------------------------------------------------------------------------------------------
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
                            await page.select_option('select#fileMonth', value="12")  # Select March
                            await page.wait_for_selector('select#fileYear', timeout=30000)
                            await page.select_option('select#fileYear', value="2024")
                            await page.click('button[role="checkbox"]')
                            file_path = r"C:\Users\DML-LT-36\Desktop\streamlit playwright\downloaded_data.xlsx"
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
                            # st.image(screenshot_path)

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
                        loop =  asyncio.run(main())
                        asyncio.set_event_loop(loop)
                        title = loop.run_until_complete(main())
                        print(title)

#--------------------------------------------------------------------------------------------------------------------
                    # Download button for Excel
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer,
                        file_name="downloaded_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                

else:
    st.warning("Please enter your API key to proceed.")
