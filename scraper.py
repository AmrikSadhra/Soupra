from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from models import SupraObj
import time
import os

TIMEOUT = 5


def init_webdriver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return webdriver.Firefox(options=options)


def handle_cookie_banner(driver_):
    try:
        WebDriverWait(driver_, TIMEOUT).until(
            ec.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()

        WebDriverWait(driver_, TIMEOUT).until(
            ec.invisibility_of_element_located((By.CLASS_NAME, "onetrust-pc-dark-filter.ot-fade-in"))
        )
        time.sleep(2)
    except (NoSuchElementException, TimeoutException):
        pass


def enter_location(driver_, postcode):
    WebDriverWait(driver_, TIMEOUT).until(
        ec.element_to_be_clickable((By.CLASS_NAME, "car-filter-item.location-filter"))
    ).click()

    postcode_element = WebDriverWait(driver_, TIMEOUT).until(
        ec.presence_of_element_located((By.ID, "postcode-filter-menu"))
    )
    postcode_element.click()
    postcode_element.send_keys(postcode)
    postcode_element.send_keys(Keys.ENTER)

    # Takes a while to load the locations, XPATH isn't valid to the <p> tag containing the info :shrug:
    time.sleep(3)


def get_html(driver_, url):
    driver_.get(url)
    handle_cookie_banner(driver_)
    enter_location(driver_, os.environ['HOME_POSTCODE'])
    return driver_.page_source


# Press the green button in the gutter to run the script.
def get_available_supras():
    driver = init_webdriver()

    supra_search_url = ("https://used.toyota.co.uk/approved-used?step=carFilter&model[]=9384&trans_type["
                        "]=4379&mileage=8000&deposit=250&term=48&monthlypay=425&payinfull=1000,"
                        "200000&depositMultiple=6&maintenance=0&financeGroupType=personal&acceptedFinance=false")
    supra_search_page = get_html(driver, supra_search_url)
    driver.quit()

    soupra = BeautifulSoup(supra_search_page, "html.parser")

    available_supras = []

    for supra in soupra.find_all('div', {'class': ['pod-data']}):
        details_list = supra.find("p", class_="car-details").text.strip().split('|')
        price_str = supra.find("span", class_="price").text.strip()
        mileage_str = supra.find("span", class_="car-mileage").text.strip()
        pod_location = supra.find("div", class_="pod-location")
        distance_str = pod_location.find("p", class_=None).text.strip()

        registration = details_list[-1].strip()
        year_full = details_list[-2].strip()
        year = year_full[0:year_full.find(' ')]
        price = int(price_str[1:].replace(',', ''))
        mileage = int(mileage_str[0:mileage_str.find(' ')].replace(',', ''))
        distance = distance_str[0:distance_str.find(' ')]
        available_supras.append(SupraObj(registration, year, price, mileage, distance))

    return available_supras
