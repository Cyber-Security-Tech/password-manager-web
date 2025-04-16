from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import urllib.request
import random

# --- CONFIG ---
URL = "https://password-manager-web-mh0f.onrender.com"
CHROMEDRIVER_PATH = "C:\\chromedriver\\chromedriver.exe"
username = f"demo_user_{random.randint(1000, 9999)}"
password = "DemoPassword123"

# --- Wake up Render ---
def wait_for_render(url, timeout=60):
    start = time.time()
    while True:
        try:
            urllib.request.urlopen(url, timeout=10)
            print("Render is awake!")
            break
        except:
            if time.time() - start > timeout:
                print("Timeout waiting for Render.")
                break
            print("Waiting for Render to wake up...")
            time.sleep(3)

# --- Setup Chrome ---
options = Options()
options.add_argument("--start-maximized")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

wait_for_render(URL)
driver.get(URL)

# --- Step 1: Go to Register ---
time.sleep(3)
driver.find_element(By.LINK_TEXT, "Register here").click()
time.sleep(2)

# --- Step 2: Fill out registration ---
driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.ID, "confirm_password").send_keys(password)
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(3)

# --- Step 3: Login with new user ---
driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(4)

# --- Step 4: Add Vault Entries ---
entries = [
    {"website": "github.com", "username": "demogit", "password": "ghp_secret123"},
    {"website": "linkedin.com", "username": "demo_linkedin", "password": "linkinP@ss"},
    {"website": "netflix.com", "username": "demo_stream", "password": "streaming123"},
]

for entry in entries:
    driver.find_element(By.ID, "website").clear()
    driver.find_element(By.ID, "website").send_keys(entry["website"])
    driver.find_element(By.ID, "login_username").clear()
    driver.find_element(By.ID, "login_username").send_keys(entry["username"])
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(entry["password"])
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

# --- Step 5: Use Search ---
driver.find_element(By.ID, "search").send_keys("netflix")
time.sleep(3)

# --- Step 6: Edit Entry ---
driver.find_element(By.LINK_TEXT, "Edit").click()
time.sleep(3)
driver.find_element(By.ID, "login_username").clear()
driver.find_element(By.ID, "login_username").send_keys("updated_user")
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(3)

# --- Step 7: Delete Entry ---
driver.find_element(By.LINK_TEXT, "Delete").click()
time.sleep(3)

# --- Step 8: Logout ---
driver.find_element(By.LINK_TEXT, "Logout").click()
time.sleep(2)

# --- Done ---
driver.quit()
