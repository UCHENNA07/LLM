from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Define the URL to visit
url = "https://www.txsmartbuy.com/esbd"
# Specify the directory where you want to download the CSV
download_directory = r"/Users/owner/Downloads"
# Set up Chrome options to handle file downloads
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
prefs = {
    "download.default_directory": download_directory,  # Set the download directory
    "download.prompt_for_download": False,             # Disable download prompt
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True                       # Enable safe browsing
}
chrome_options.add_experimental_option("prefs", prefs)
# Specify the path to the ChromeDriver executable
webdriver_path = "/path/to/chromedriver"
# Set up the WebDriver service
service = Service()
# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)
try:
    # Navigate to the URL
    driver.get(url)

    driver.maximize_window()
    # Allow the page to load
    time.sleep(20)

    WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'esbd-result-title'))
                )
    # Locate the "Export to CSV" button using its class name and other attributes

    wait = WebDriverWait(driver, 30)  # Wait up to 20 seconds
    # export_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='browse-contract-search-actions']//button[@data-action='export-csv']")))
    
    full_x_path = '/html/body/div/div/div/div/div[3]/div/div/form/div[11]/button[3]'
    button = driver.find_element(By.XPATH, value= full_x_path)

    # Step 4: Click the button
    button.click()
    # # Scroll into view and click using JavaScript
    # driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
    # time.sleep(2)  # Allow scroll
    # driver.execute_script("arguments[0].click();", export_button)
    # Wait for the download to complete (you may adjust the time based on download speed)
    time.sleep(85)
finally:
    # Quit the WebDriver
    driver.quit()
# Verify if the file has been downloaded
downloaded_files = os.listdir(download_directory)
print("Downloaded files:", downloaded_files)
