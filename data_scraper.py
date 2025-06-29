# data_scraper.py - This script will be run by the GitHub Action.
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
# These will be set as environment variables in the GitHub Action for security.
QC_USERNAME = os.environ.get("QC_USERNAME")
QC_PASSWORD = os.environ.get("QC_PASSWORD")
QC_PROJECT_URL = "https://www.quantconnect.com/project/28418589" # Your project URL
OUTPUT_FILE = "data/SPY_1second_data.csv" # The file to save data to in your repo

# --- Setup Selenium Webdriver ---
chrome_options = Options()
chrome_options.add_argument("--headless") # Run Chrome in the background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

try:
    # --- 1. Log In to QuantConnect ---
    print("Navigating to QuantConnect login page...")
    driver.get("https://www.quantconnect.com/login")
    
    # Wait for the login form to be visible and fill it out
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "Username"))).send_keys(QC_USERNAME)
    driver.find_element(By.ID, "Password").send_keys(QC_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
    print("Login submitted.")

    # --- 2. Navigate to the Research Notebook ---
    print(f"Waiting for login and navigating to project URL: {QC_PROJECT_URL}")
    time.sleep(10) # Wait for login to process and cookies to be set
    driver.get(f"{QC_PROJECT_URL}#research.ipynb")

    # --- 3. Run the Notebook to Generate Data ---
    print("Running the research notebook...")
    # Wait for the 'Run All' button to be clickable, then click it.
    run_all_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Run All']")))
    run_all_button.click()
    print("Notebook is running. Waiting for data output...")

    # --- 4. Scrape the Data from the Log Output ---
    # Wait up to 10 minutes for the 'END OF CSV DATA' message to appear in the logs.
    # This gives QC time to fetch and print all the 1-second data.
    end_log_locator = (By.XPATH, "//*[contains(text(), 'END OF CSV DATA')]")
    WebDriverWait(driver, 600).until(EC.visibility_of_element_located(end_log_locator))
    print("Data generation complete. Scraping log output...")

    # Get the entire log panel's text content
    log_panel = driver.find_element(By.CSS_SELECTOR, ".compiler-output-log")
    full_log_text = log_panel.text

    # Extract just the CSV data between our start and end markers
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

finally:
    driver.quit()
