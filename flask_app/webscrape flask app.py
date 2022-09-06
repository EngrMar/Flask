from flask import Flask, render_template, redirect, url_for, send_file
from flask_restful import Api, Resource
from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import range
from flask import request
import uuid
import glob
import os

app = Flask(__name__)

#################################################################################################
path = Service(r"C:\Users\marion.deguzman\PycharmProjects\chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=path, options=options)
#################################################################################################

###WEBAPP
@app.route('/')
def hello_world():
    return render_template("index_2.html")

#################################################################################################
@app.route("/yp_bd")
def yp_busdir():
    #return "Under construction"
    ##Yellow Page Login
    driver.get("https://www.yellow-pages.ph/login")
    email_login = driver.find_element(By.NAME, "yp_user[email]")
    email_login.send_keys("marion.deguzman@imadzsolutions.com")
    password_login = driver.find_element(By.NAME, "yp_user[password]")
    password_login.send_keys("imadzmarion@0829")
    sign_in = driver.find_element(By.NAME, "commit")
    sign_in.click()
    ##Yellow page login -> Accept Cookies to proceed
    accept_cookies = driver.find_element(By.LINK_TEXT, "I ACCEPT")
    accept_cookies.click()
    ##Yellow page -> click browse by category
    browse_by_cat = driver.find_element(By.LINK_TEXT, "Browse by Category")
    browse_by_cat.click()
    time.sleep(10)
    ##Categories
    Business_Categories_WE = []
    categories = driver.find_elements(By.XPATH, '//a[@class="category-item d-flex ml-2 mr-md-3 ml-md-1 p-1 text-dark yp-click"]')
    for business_cat in categories:
        cat_we = business_cat
        Business_Categories_WE.append(cat_we)
    return render_template("categories_yp.html", cat_WE=Business_Categories_WE)

@app.route("/Business/Categories/YP", methods=["POST", "GET"])
def bus_cat_yp():
    yp_dict = {}
    yp_name = []
    yp_email = []
    yp_contacts = []
    business_categories_pages = []
    company_names_link = []
    company_scraped_data = pd.DataFrame()
    for_dl = ''
    if request.method == "GET":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@rel="next"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        return render_template("selected_category_yp.html", business_page=business_categories_pages, nmberofpges=size)
    elif request.method == "POST":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@rel="next"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        chosen_extent = request.form['extent']
        for page in business_categories_pages:
            if business_categories_pages.index(page) <= int(chosen_extent) - 1:
                driver.get(page)
                business_link = driver.find_elements(By.XPATH, '//a[@class="yp-click"]')
                for business_names in business_link:
                    links = business_names.get_attribute("href")
                    company_names_link.append(links)
            else:
                break
        size_of_business_list_chosen = len(company_names_link)
        for info in company_names_link:
            n = company_names_link.index(info)
            m = int(size_of_business_list_chosen) - 1
            if n <= m:
                response = requests.get(company_names_link[n])
                web_page = response.text
                soup = BeautifulSoup(web_page, "html.parser")
                email = soup.find(name="a", class_="biz-link d-block ellipsis yp-click email-link")
                if email == None:
                    yp_email.append("No Data Source")
                else:
                    yp_email.append(email.get("href"))
                contacts = soup.find(name="span", class_="phn-txt")
                if contacts == None:
                    yp_contacts.append("No Data from Source")
                else:
                    yp_contacts.append(contacts.getText())
                name = soup.find(name="div", class_="header-name-container d-flex")
                if name == None:
                    yp_name.append("No Data from Source")
                else:
                    yp_name.append(name.h1.getText())
                yp_dict[n] = {
                    "name": yp_name[n],
                    "email": yp_email[n],
                    "contact_number": yp_contacts[n]
                }
            else:
                break
        company_scraped_data = pd.DataFrame(yp_dict).T
        file_name = f"scraped-data_yp_{uuid.uuid4()}.csv"
        for_dl = company_scraped_data.to_csv(file_name)
        return render_template("selected_category_half_yp.html", company_data=company_scraped_data, file_for_dl=for_dl)

@app.route("/download/bs", methods=["POST", "GET"])
def csv_download_yp():
    if request.method == "GET":
        file_dir = glob.glob(r"C:\Users\marion.deguzman\PycharmProjects\pythonProject3\*.csv")
        latest_file = max(file_dir, key=os.path.getctime)
        return send_file(latest_file, as_attachment=True)



#################################################################################################

@app.route("/bl_bd")
def BL_busdir():
    #Login
    driver.get("https://www.businesslist.ph/")
    email_login = driver.find_element(By.LINK_TEXT, "Sign in")
    email_login.click()
    time.sleep(5)
    email_login_username = driver.find_element(By.XPATH, '//input[@name="data[Login][username]"]')
    email_login_username.send_keys("marion.deguzman")
    password_login = driver.find_element(By.XPATH, '//input[@type="password"]')
    password_login.send_keys("HirayaManawari0829")
    sign_in_submit = driver.find_element(By.XPATH, '//input[@type="submit"]')
    sign_in_submit.click()
    business_list_icon = driver.find_element(By.CSS_SELECTOR, "nav a")
    business_list_icon.click()
    time.sleep(10)
    see_all_icon = driver.find_element(By.LINK_TEXT, "See All")
    see_all_icon.click()
    time.sleep(5)
    #Categories
    Business_Categories = []
    Business_Categories_WE = []
    categories = driver.find_elements(By.CSS_SELECTOR, "main ul li a")
    for business_cat in categories:
        cat_we = business_cat
        Business_Categories_WE.append(cat_we)
    return render_template("categories_bl.html", cat_WE=Business_Categories_WE)

@app.route("/Business/Categories/BL", methods=["POST", "GET"])
def bus_cat_bl():
    BusinessList_dict = {}
    BL_name = []
    BL_website = []
    BL_contact_number = []
    BL_contact_person = []
    business_categories_pages = []
    company_names_link = []
    company_scraped_data = pd.DataFrame()
    for_dl = ''
    if request.method == "GET":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@rel="next"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        return render_template("selected_category_bl.html", business_page=business_categories_pages, nmberofpges=size)
    elif request.method == "POST":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@rel="next"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        chosen_extent = request.form['extent']
        for page in business_categories_pages:
            if business_categories_pages.index(page) <= int(chosen_extent) - 1:
                driver.get(page)
                business_link = driver.find_elements(By.CSS_SELECTOR, "h4 a")
                for business_names in business_link:
                    links = business_names.get_attribute("href")
                    company_names_link.append(links)
            else:
                break
        size_of_business_list_chosen = len(company_names_link)
        for info in company_names_link:
            n = company_names_link.index(info)
            m = int(size_of_business_list_chosen) - 1
            if n <= m:
                response = requests.get(company_names_link[n])
                web_page = response.text
                soup = BeautifulSoup(web_page, "html.parser")
                website = soup.find(name="div", class_="text weblinks")
                if website == None:
                    BL_website.append(website)
                else:
                    BL_website.append(website.a.get("href"))
                contact_number = soup.find(name="div", class_="text phone")
                if contact_number == None:
                    BL_contact_number.append("No Data from Source")
                else:
                    BL_contact_number.append(contact_number.getText())
                name = soup.find(id="company_name")
                if name == None:
                    BL_name.append("No Data from Source")
                else:
                    BL_name.append(name.getText())

                BusinessList_dict[n] = {
                    "Name": BL_name[n],
                    "website": BL_website[n],
                    "contact_number": BL_contact_number[n]
                }
            else:
                break
        company_scraped_data = pd.DataFrame(BusinessList_dict).T
        file_name = f"scraped-data_bl_{uuid.uuid4()}.csv"
        for_dl = company_scraped_data.to_csv(file_name)
    return render_template("selected_category_half_bl.html", company_data=company_scraped_data, file_for_dl=for_dl)

@app.route("/download/bl", methods=["POST", "GET"])
def csv_download_bl():
    if request.method == "GET":
        file_dir = glob.glob(r"C:\Users\marion.deguzman\PycharmProjects\pythonProject3\*.csv")
        latest_file = max(file_dir, key=os.path.getctime)
        return send_file(latest_file, as_attachment=True)

#################################################################################################
@app.route("/bs_bd")
def BS_busdir():
    driver.get("https://business.sulit.ph/")
    email_login = driver.find_element(By.LINK_TEXT, "Login")
    email_login.click()
    email_login_username = driver.find_elements(By.XPATH, '//input[@class="required"]')[0]
    email_login_username.send_keys("marion.deguzman")
    password_login = driver.find_elements(By.XPATH, '//input[@class="required"]')[1]
    password_login.send_keys("HirayaManawari0829")
    sign_in_submit = driver.find_element(By.XPATH, '//input[@type="submit"]')
    sign_in_submit.click()
    page_parsed = driver.page_source
    soup = BeautifulSoup(page_parsed, "html.parser")
    Business_Categories_Links = []
    Business_Categories_Names = []
    Business_Categories_WE = []
    business_categories = soup.find_all(name="div", class_="parent-cat-wrap column column-block")
    for business_cat in business_categories:
        link = business_cat.a.get("href")
        name = business_cat.a.getText()
        Business_Categories_Links.append(link)
        Business_Categories_Names.append(name)
        Business_Categories_WE.append(business_cat.a)
    return render_template("categories_bs.html", cat_we=Business_Categories_WE)

@app.route("/Business/Categories/BS", methods=["POST", "GET"])
def bus_cat():
    BusinessList_dict = {}
    BS_name = []
    BS_email = []
    BS_contact_number = []
    business_categories_pages = []
    company_names_link = []
    company_scraped_data = pd.DataFrame()
    for_dl = ''
    if request.method == "GET":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@class="next page-numbers"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        return render_template("selected_category_bs.html", business_page=business_categories_pages, nmberofpges=size)
    elif request.method == "POST":
        business_category_chosen = request.args['Category_Link']
        driver.get(business_category_chosen)
        time.sleep(10)
        business_categories_pages.append(business_category_chosen)
        while True:
            try:
                next_page_element = driver.find_element(By.XPATH, '//a[@class="next page-numbers"]')
                next_page_url = next_page_element.get_attribute("href")
                driver.get(next_page_url)
                business_categories_pages.append(driver.current_url)
            except NoSuchElementException:
                break
        size = len(business_categories_pages)
        chosen_extent = request.form['extent']
        for page in business_categories_pages:
            if business_categories_pages.index(page) <= int(chosen_extent) - 1:
                driver.get(page)
                business_link = driver.find_elements(By.CSS_SELECTOR, "header h4 a")
                for business_names in business_link:
                    links = business_names.get_attribute("href")
                    company_names_link.append(links)
            else:
                break
        size_of_business_list_chosen = len(company_names_link)
        for info in company_names_link:
            n = company_names_link.index(info)
            m = int(size_of_business_list_chosen) - 1
            if n <= m:
                response = requests.get(company_names_link[n])
                web_page = response.text
                soup = BeautifulSoup(web_page, "html.parser")
                email = soup.find(name="li", id="listing-email")
                if email == None:
                    BS_email.append("No Data Source")
                else:
                    BS_email.append(email.a.get("href"))
                contact_number = soup.find(name="a", class_="text-muted")
                if contact_number == None:
                    BS_contact_number.append("No Data from Source")
                else:
                    BS_contact_number.append(contact_number.getText())
                name = soup.find(name="h1", class_="entry-title")
                if name == None:
                    BS_name.append("No Data from Source")
                else:
                    BS_name.append(name.getText())
                BusinessList_dict[n] = {
                    "Name": BS_name[n],
                    "email": BS_email[n],
                    "contact_number": BS_contact_number[n]
                }
            else:
                break
        company_scraped_data = pd.DataFrame(BusinessList_dict).T
        file_name = f"scraped-data_bs_{uuid.uuid4()}.csv"
        for_dl = company_scraped_data.to_csv(file_name)
    return render_template("selected_category_half_bs.html", company_data=company_scraped_data, file_for_dl=for_dl)

@app.route("/download/bs", methods=["POST", "GET"])
def csv_download():
    if request.method == "GET":
        file_dir = glob.glob(r"C:\Users\marion.deguzman\PycharmProjects\pythonProject3\*.csv")
        latest_file = max(file_dir, key=os.path.getctime)
        return send_file(latest_file, as_attachment=True)

#################################################################################################

@app.route("/FAQ")
def FAQ():
    return "This page contains FAQs"


if __name__ == "__main__":
    app.run(debug=True, threaded=True)