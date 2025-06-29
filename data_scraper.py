# data_scraper.py - Updated with advanced options and better debugging.

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Configuration ---
QC_USERNAME = os.environ.get("QC_USERNAME")
QC_PASSWORD = os.environ.get("QC_PASSWORD")
QC_PROJECT_URL = "https://www.quantconnect.com/project/28418589"
OUTPUT_FILE = "data/SPY_1minute_data.csv"
SCREENSHOT_FILE = "debug_screenshot.png"

# --- Setup Selenium Webdriver (with Advanced Options from your research) ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(60) # Set a 60 second timeout for page loads

try:
    # --- 1. Log In to QuantConnect ---
    print("Navigating to QuantConnect login page...")
    driver.get("https://www.quantconnect.com/login")

    # ** NEW DEBUGGING STEP **
    # Wait a few seconds for any "checking browser" screens to pass, then take a screenshot.
    print("Waiting for page to load...")
    time.sleep(5)
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    driver.save_screenshot("login_page_view.png")
    print("Screenshot of the login page has been saved as login_page_view.png")
    
    # Wait for the login form to be visible and fill it out
    print("Attempting to find and fill login form...")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Username"))).send_keys(QC_USERNAME)
    driver.find_element(By.ID, "Password").send_keys(QC_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
    print("Login submitted.")

    # --- 2. Navigate to the Research Notebook ---
    print(f"Waiting for login and navigating to project URL: {QC_PROJECT_URL}#research.ipynb")
    time.sleep(15) # Increase wait time after login
    driver.get(f"{QC_PROJECT_URL}#research.ipynb")

    # --- 3. Run the Notebook to Generate Data ---
    print("Running the research notebook to generate data...")
    run_all_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Run All']")))
    run_all_button.click()
    print("Notebook is running. Waiting for data output...")

    # --- 4. Scrape the Data from the Log Output ---
    end_log_locator = (By.XPATH, "//*[contains(text(), 'END OF CSV DATA')]")
    WebDriverWait(driver, 600).until(EC.visibility_of_element_located(end_log_locator))
    print("Data generation complete. Scraping log output...")

    log_panel = driver.find_element(By.CSS_SELECTOR, ".compiler-output-log")
    full_log_text = log_panel.text
    
    start_marker = "--- COPY THE CSV DATA BELOW ---\n"
    end_marker = "\n--- END OF CSV DATA ---"
    start_index = full_log_text.find(start_marker) + len(start_marker)
    end_index = full_log_text.find(end_marker)
    csv_data = full_log_text[start_index:end_index]

    if not csv_data:
        raise Exception("Could not find CSV data in the log output.")
        
    print(f"Successfully scraped {len(csv_data.splitlines())} lines of data.")

    # --- 5. Save the Data to a File ---
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(csv_data)
    print(f"Data successfully saved to {OUTPUT_FILE}")

except Exception as e:
    # If ANY error occurs, save a final screenshot.
    print(f"An error occurred: {str(e)}")
    driver.save_screenshot(SCREENSHOT_FILE)
    print(f"Error screenshot saved to {SCREENSHOT_FILE}")
    raise e

finally:
    driver.quit()
