from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time
from amazoncaptcha import AmazonCaptcha

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.amazon.com/errors/validateCaptcha")

link = driver.find_element(By.TAG_NAME, "img").get_attribute("src")

captcha = AmazonCaptcha.fromlink(link)

captcha_value = AmazonCaptcha.solve(captcha)

print(captcha_value)

text_field = driver.find_element(By.ID, "captchacharacters")

text_field.send_keys(captcha_value)

button = driver.find_element(By.TAG_NAME, "button")
button.click()

time.sleep(10)

driver.quit()