from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up the WebDriver (Chrome in this case)
options = webdriver.ChromeOptions()

options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Function to log in with phone number and password
def start_driver(phone_number, password):

    driver.get("https://account.cellphones.com.vn/")

    time.sleep(2)

    phone_input = driver.find_element(By.XPATH, "//form[@class = 'm-3']//input[@type = 'tel']")  # Update with correct ID if needed
    phone_input.send_keys(phone_number)

    password_input = driver.find_element(By.XPATH, "//form[@class = 'm-3']//input[@type = 'password']")  # Update with correct ID if needed
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, "//button[@class= 'btn-form__submit is-fullwidth button__login']")
    login_button.click()

    time.sleep(5)

    if "account" not in driver.current_url:
        print("Successfully logged in!")
    else:
        print("Login failed!")
    return driver


def navigate_to_main_website(driver):
    time.sleep(2)
    driver.get("https://cellphones.com.vn/")

def get_cookies(driver):
    # Extract cookies and convert to a dictionary format
    cookies = driver.get_cookies()
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    return session_cookies

def login(phone, pw):
    driver = start_driver(phone, pw)
    navigate_to_main_website(driver)
    cookies = get_cookies(driver)
    driver.quit()
    return cookies





