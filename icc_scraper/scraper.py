import time

from selenium import webdriver
import chromedriver_autoinstaller

from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import threading
import unicodedata
import json
# import docx2pdf
import requests
import glob

#make a 'login.txt' file in the same directory with your GT username on the firstline and password on second
try:
    with open("../cios/login.txt", "r") as LOGIN:
        USERNAME = LOGIN.readline().rstrip()
        PASSWORD = LOGIN.readline().rstrip()
        LOGIN.close()
except:
    raise Exception("CANNOT PROCEED, No login.txt file found")

chromedriver_autoinstaller.install()

DRIVER = webdriver.Chrome()
DEBUG_MODE = False
WAIT = WebDriverWait(DRIVER, 25)

def goToICC():
    DRIVER.get("https://icc.gatech.edu/")
    #return error_handler(element_to_find="username", method_to_find="name", purpose="Selecting GT")
    return print("accessed icc")

def loginGT():
    gatech_login_username = DRIVER.find_element_by_name("username")
    gatech_login_password = DRIVER.find_element_by_name("password")

    gatech_login_username.send_keys(USERNAME)
    gatech_login_password.send_keys(PASSWORD)

    submit_button = DRIVER.find_element_by_name("submit")
    submit_button.click()

    print("Please authenticate on Duo")
    WAIT.until(lambda DRIVER: DRIVER.find_element_by_id("lnkSeeResultsImg"))
    #return error_handler(element_to_find="duo_form", method_to_find="id", purpose="Logging In")
    return print("accessed Duo form")

def goToDept(dept):
    link = DRIVER.find_elements_by_id(dept)
    link[0].click()
    print("going to " + dept)
    WAIT.until(lambda DRIVER: DRIVER.find_elements_by_xpath("//*[contains(text(), '{0}-')]".format(dept)) or DRIVER.find_elements_by_xpath("//*[contains(text(), 'No {0} syllabi uploaded')]".format(dept)))

def goToLetter(letter): # must be capital letter
    DRIVER.execute_script("document.getElementById('filtersc').style.display = 'block';")
    select = Select(DRIVER.find_element_by_id("filtersc"))
    select.select_by_value(letter)

def findDepts():
    pageSource = DRIVER.page_source
    soup = BeautifulSoup(pageSource, 'html.parser')
    ids = [tag['id'] for tag in soup.find('div', {'id': 'sylmenu'}).select("a")]
    return ids

def downloadLink(url, filename):
    response = requests.get(url, stream = True)
    ext = "." + url.split(".")[-1]
    with open(filename + ext, 'wb') as file:
        for chunk in response.iter_content(1024 * 8):
            if chunk:
                file.write(chunk)
                file.flush()
                os.fsync(file.fileno())
    
    # if (ext == ".docx" or ext == ".doc"):
    #     convert(filename + ext, filename + ".pdf")
    #     os.remove(filename + ext)

def downloadDeptLinks(dept, override = False):
    print("currently scraping " + dept)
    soup = BeautifulSoup(DRIVER.page_source, 'html.parser')
    root = DRIVER.current_url
    urllist = soup.find('div', {'id': 'syllist'}).select("a")
    urllist = [[i.get_text(), urljoin(root, i['href'])] for i in urllist]
    if len(urllist) > 0:
        try:
            os.mkdir("icc/" + dept.lower())
        except:
            pass    
    for url in urllist:
        filename = "icc/" + dept.lower() + "/" + dept.lower() + url[0].split("-")[-1]
        if override or not glob.glob(filename + ".*"):
            downloadLink(url[1], filename)
    print("found " + str(len(urllist)) + " syllabi")

def downloadAll(pickup = False):
    count = 0
    goToLetter("*")
    depts = findDepts()
    if pickup:
        depts = depts[depts.index(pickup)+1:]
    for dept in depts:
        goToDept(dept)
        downloadDeptLinks(dept)
        count += 1
    print(str(count) + " depts syllabi downloaded")


    
    
