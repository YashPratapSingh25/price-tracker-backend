from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from amazoncaptcha import AmazonCaptcha
from models.TrackedProductModel import TrackedProduct
import firebase_methods
import time
import datetime

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def amazon_captcha_solver(src : str, driver):
    captcha = AmazonCaptcha.fromlink(src)
    captcha_value = AmazonCaptcha.solve(captcha)

    captcha_text_field = driver.find_element(By.ID, "captchacharacters")
    captcha_text_field.send_keys(captcha_value)

    button = driver.find_element(By.TAG_NAME, "button")
    button.click()


def deals_scraping():

    deals = []

    
    driver.get("https://www.amazon.in/b?node=30631803031&ref_=a2i_ohl_gw_cml_cta")

    try:
        captcha_link = driver.find_element(By.TAG_NAME, "img").get_attribute("src")
        amazon_captcha_solver(src=captcha_link, driver=driver)
    except:
        pass
    
    products = driver.find_elements(By.CSS_SELECTOR, "div._octopus-search-result-card_style_apbSearchResultItem__2-mx4")

    if len(products) == 0:
        driver.refresh()
        products = driver.find_elements(By.CSS_SELECTOR, "div._octopus-search-result-card_style_apbSearchResultItem__2-mx4")

    for product in products:

        info = {
            "image": product.find_element(By.TAG_NAME, "img").get_attribute("src"),
            "title" : product.find_element(By.CSS_SELECTOR, "h2 > span").text,
            "current_price" : product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text,
            "previous_price" : product.find_element(By.CSS_SELECTOR, "span[data-a-strike='true']").text.replace("₹", ""),
            "link" : product.find_element(By.TAG_NAME, "a").get_attribute("href")
        }

        deals.append(info)

    return deals

def amazon_scraping(search_query):

    driver.get("https://www.amazon.in/")

    amazon_list = []

    try:
        captcha_link = driver.find_element(By.TAG_NAME, "img").get_attribute("src")
        amazon_captcha_solver(src=captcha_link, driver=driver)
    except:
        pass

    text_field = driver.find_element(By.ID, "twotabsearchtextbox")
    text_field.send_keys(search_query + Keys.ENTER)

    products = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

    i = 0
    products_shown = 0
    while products_shown < 5:

        product_image = products[i].find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")

        product_name = products[i].find_element(By.CSS_SELECTOR, "div[role='listitem'] h2.a-color-base").get_attribute("aria-label")

        try:
            product_price = products[i].find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        except:
            i += 1
            continue

        product_link = products[i].find_element(By.CSS_SELECTOR, "a.a-link-normal").get_attribute("href")

        if product_name.find("Sponsored Ad") == 0:
            i += 1
            continue

        product_info = {
            "image": product_image,
            "title": product_name,
            "price": product_price,
            "link": product_link,
            "site": "Amazon"
        }

        amazon_list.append(product_info)

        i += 1
        products_shown += 1

    return amazon_list


def flipkart_scraping(search_query):

    driver.get("https://www.flipkart.in/")

    try:
        text_field = driver.find_element(By.CSS_SELECTOR, "input[title = 'Search for Products, Brands and More']")
        text_field.send_keys(search_query + Keys.ENTER)
    except:
        driver.refresh()
        text_field = driver.find_element(By.CSS_SELECTOR, "input[title = 'Search for Products, Brands and More']")
        text_field.send_keys(search_query + Keys.ENTER)

    flipkart_list = []

    is_clothing = False


    try:
        time.sleep(5)
        button = driver.find_element(By.TAG_NAME, "button")
        button.click()
    except:
        pass

    is_grid = True
    products = driver.find_elements(By.CLASS_NAME, "slAVV4")

    if len(products) == 0:
        is_grid = False
        products = driver.find_elements(By.CLASS_NAME, "tUxRFH")

    if(len(products) == 0):
        is_clothing = True
        products = driver.find_elements(By.CLASS_NAME, "LFEi7Z")

    i = 0
    products_shown = 0

    while products_shown < 5:

        try:
            if is_clothing : products[i].find_element(By.CSS_SELECTOR, "div._2ABVdq")
            elif is_grid : products[i].find_element(By.CSS_SELECTOR, "div.xgS27m")
            else : products[i].find_element(By.CSS_SELECTOR, "div.f8qK5m")
            i += 1
            continue
        except:
            pass
        
        if is_clothing:
            product_image = products[i].find_element(By.TAG_NAME, "img").get_attribute("src")
            product_name = products[i].find_element(By.CLASS_NAME, "WKTcLC").text
            product_price = products[i].find_element(By.CLASS_NAME, "Nx9bqj").text
            product_link = products[i].find_element(By.CLASS_NAME, "WKTcLC").get_attribute("href")

        elif is_grid:
            product_image = products[i].find_element(By.CSS_SELECTOR, "img.DByuf4").get_attribute("src")
            product_name = products[i].find_element(By.CSS_SELECTOR, "a.wjcEIp").get_attribute("title")
            product_price = products[i].find_element(By.CSS_SELECTOR, "div.Nx9bqj").text
            product_link = products[i].find_element(By.CSS_SELECTOR, "a.VJA3rP").get_attribute("href")
        else:
            product_image = products[i].find_element(By.CSS_SELECTOR, "img.DByuf4").get_attribute("src")
            product_name = products[i].find_element(By.CSS_SELECTOR, "div.KzDlHZ").text
            product_price = products[i].find_element(By.CSS_SELECTOR, "div.Nx9bqj").text
            product_link = products[i].find_element(By.CSS_SELECTOR, "a.CGtC98").get_attribute("href")

        product_info = {
            "image": product_image,
            "title": product_name,
            "price": product_price.removeprefix("₹"),
            "link": product_link,
            "site": "Flipkart"
        }

        flipkart_list.append(product_info)

        i += 1
        products_shown += 1

    return flipkart_list

async def fetch_amazon_product(productUrl : str, currentUser : str) -> str:
    
    driver.get(productUrl)

    try:
        captcha_link = driver.find_element(By.TAG_NAME, "img").get_attribute("src")
        amazon_captcha_solver(captcha_link, driver)
    except:
        pass

    title = driver.find_element(By.ID, "productTitle").text
    prices = driver.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
    imageUrl = driver.find_element(By.CSS_SELECTOR, "div#imgTagWrapperId img").get_attribute("src")

    current_price = ""
    for price in prices:
        if price.text != "":
            current_price = price.text
            break;
    
    docId = f"{title} Amazon".replace(" ", "_").replace("/", "`")

    if await firebase_methods.is_product_tracked(docId):
        return "Exists"

    product = TrackedProduct(
        docId = docId,
        imageUrl = imageUrl,
        title = title,
        currentPrice = current_price,
        prevPrice = current_price,
        dateAdded = datetime.datetime.now().isoformat(),
        lastUpdated = datetime.datetime.now().isoformat(),
        productUrl = productUrl,
        currentUser = currentUser,
        site = "Amazon",
    )

    await firebase_methods.add_product(product=product)
    return "Added"

async def fetch_flipkart_product(productUrl : str, currentUser : str) -> str:

    driver.get(productUrl)

    title = ""
    
    try:
        title = driver.find_element(By.CSS_SELECTOR, "span.VU-ZEz").text
    except:
        time.sleep(5)
        button = driver.find_element(By.CSS_SELECTOR, "button.btn")
        button.click()
        driver.refresh()
        title = driver.find_element(By.CSS_SELECTOR, "span.VU-ZEz").text

    index = title.find("  ")
    if(index != -1) : title = title[:index].strip()

    current_price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text.removeprefix("₹")
    imageUrl = driver.find_element(By.CSS_SELECTOR, "img.DByuf4").get_attribute("src")

    docId = f"{title} Flipkart".replace(" ", "_").replace("/", "`")

    if await firebase_methods.is_product_tracked(docId):
        return "Exists"

    product = TrackedProduct(
        docId = docId,
        imageUrl = imageUrl,
        title = title,
        currentPrice = current_price,
        prevPrice = current_price,
        dateAdded = datetime.datetime.now().isoformat(),
        lastUpdated= datetime.datetime.now().isoformat(),
        productUrl = productUrl,
        currentUser = currentUser,
        site = "Flipkart",
    )

    await firebase_methods.add_product(product=product)
    return "Added"

async def fetch_latest_price(url : str):
    current_price = ""
    if url.startswith("https://www.amazon.in/"):
        try:
            captcha_link = driver.find_element(By.TAG_NAME, "img").get_attribute("src")
            amazon_captcha_solver(src=captcha_link, driver=driver)
        except:
            pass

        prices = driver.find_elements(By.CSS_SELECTOR, "span.a-price-whole")
        for price in prices:
            if price.text != "":
                current_price = price.text
                break
        
    elif url.startswith("https://www.flipkart.com/"):
        try:
            current_price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text.removeprefix("₹")
        except:
            time.sleep(5)
            button = driver.find_element(By.CSS_SELECTOR, "button.btn")
            button.click()
            driver.refresh()
            current_price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text.removeprefix("₹")

        current_price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text.removeprefix("₹")
    
    return current_price


async def fetch_latest_price_from_app(userId : str):

    docs = await firebase_methods.fetch_all_documents(userId)
    for doc in docs:
        product = doc.to_dict()
        url : str = product["productUrl"]
        driver.get(url)

        current_price = await fetch_latest_price(url)

        await firebase_methods.update_price(doc.id, current_price)

    return docs