import sys
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def fetch_page_source(driver, url):
    """
    Navigates to the URL and retrieves the page source after elements load.
    """
    try:
        driver.get(url)
        # Wait for the main content (form/table) to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        # Extra sleep to ensure dynamic price or image elements are rendered
        time.sleep(3) 
        return driver.page_source
    except TimeoutException:
        print(f"Timeout: Page took too long to load at {url}")
        return None
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

def perform_login(driver, email, password, main_url):
    """
    Handles the authentication flow for the website.
    """
    driver.get(main_url)
    try: 
        # Trigger login modal
        login_trigger = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div/a[1]"))
        )
        login_trigger.click()
        
        # Enter credentials
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "input_email"))
        ).send_keys(email)
        driver.find_element(By.ID, "input_password").send_keys(password)
        
        # Click login button
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or @type='submit']").click()
        
        # Verify success
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(),"Welcome back")]'))
        )
        print("Login successful")
        return True
    except Exception as e:
        print(f"Login Failed: {str(e)}")
        return False