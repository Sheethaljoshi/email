from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
driver = webdriver.Chrome()

# Open the base URL
driver.get("https://www.intercom.com/customers")  # Replace with the base URL of the website
#data-testid="cta-link-read-story"
# Function to get hrefs from the current page
def get_hrefs_from_page():
    hrefs = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, '//a[contains(@data-testid, "cta-link-read-story")]')]
    return hrefs

# Function to click the "next" button
def click_next_button():
    try:
        next_button = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "pagination__next")]'))  # Adjust the XPath for the "next" button
        )
        print(next_button)
        next_button.click()
        print("went to next page")
        return True
    except:
        print("no went to next page")
        return False

# Function to scrape hrefs from all pages
def scrape_all_pages():
    all_hrefs = []
    while True:
        time.sleep(20)  # Wait for the page to load
        hrefs = get_hrefs_from_page()
        all_hrefs.extend(hrefs)
        if not click_next_button():
            break  # Break the loop if no more next button is found
    return all_hrefs

# Scrape all pages and print the hrefs
all_hrefs = scrape_all_pages()
print(all_hrefs)
print(len(all_hrefs))
# Close the browser
driver.quit()

# Function to save HTML content from a URL to a temporary file and return the file path
def save_html_to_tempfile(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8')
        temp_file.write(response.text)
        temp_file.close()
        print(f'Successfully saved {url} to {temp_file.name}')
        return temp_file.name
    except requests.exceptions.RequestException as e:
        print(f'Failed to retrieve {url}: {e}')
        return None

# List to hold the paths of temporary HTML files
temp_files = []
client = OpenAI()
vector_store_files = client.beta.vector_stores.files.list(
  vector_store_id="vs_VwMZZPLE2n0cmHr0oqSgFzGL"
)
print(vector_store_files)
for vector_store_file in vector_store_files:
            deleted = client.beta.vector_stores.files.delete(
                vector_store_id='vs_VwMZZPLE2n0cmHr0oqSgFzGL',
                file_id=vector_store_file.id
            )
            client.files.delete(vector_store_file.id)
            print("deleted",deleted.id)
# Save HTML content from each href to a temporary HTML file\
for href in all_hrefs:
    temp_file_path = save_html_to_tempfile(href)
    if temp_file_path:
        temp_files.append(temp_file_path)
print("Temporary HTML files created:")
print(temp_files)

client_files = [client.files.create(file=open(path, "rb"),purpose="assistants") for path in temp_files]

for file in client_files:
    vector_store_file = client.beta.vector_stores.files.create(
    vector_store_id="vs_VwMZZPLE2n0cmHr0oqSgFzGL",
    file_id=file.id
    )
    print(vector_store_file)


#vs_VwMZZPLE2n0cmHr0oqSgFzGL




