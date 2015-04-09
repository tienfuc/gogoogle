from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from urllib import quote_plus
import re, os, random
from time import sleep

from user import USER, PASSWORD, PROJECT, FOLDER, VIRTUAL_DISPLAY

import sys

DEBUG = False

def create_project(driver):
    # wait for project creation
    max_retries = 30
    while True:
        sleep(1)
        try:
            project_id = driver.find_element_by_css_selector("b[class=\"ng-binding\"]").text
            if project_id:
                print "Project creation done with id: %s" % project_id
                return project_id
        except:
            pass

        max_retries -= 1
        if max_retries < 0:
            raise Exception("Project creation failed with name: %s" % PROJECT)

def delay_send_keys(element, keys):
    delay1 = round(random.uniform(0.5, 2), 2)
    print "Delay %.2f after send_keys(): %s" % (delay1, keys)
    for k in list(keys):
        delay2 = round(random.uniform(0, 0.2), 2)
        sleep(delay2)
        element.send_keys(k)
    sleep(delay1)

def spoof_click(driver):
    items = driver.find_elements_by_xpath("//dt[contains(@class, \"p6n-tree-node ng-scope ng-isolate-scope\")]/div/div/div/a/span[@class=\"ng-binding\"]/..")
    for item in random.sample(items, 4):
        attr = item.get_attribute("pan-nav-tooltip") or item.get_attribute("title")

        print "Spoof click: %s" % (attr)
        span = item.find_element_by_xpath("span")
        if not span.is_displayed():
            top = item.find_element_by_xpath("../../../../../../../preceding-sibling::*[1]")
            print "Spoof click top: %s" % top.text 
            if top.is_displayed():
                top.click()

        if span.is_displayed():
            span.click()
    
    return

def delay_get(driver, url):
    delay = round(random.uniform(3, 5), 2)
    print "Delay %.2f after get(): %s" % (delay, url)
    driver.get(url)
    sleep(delay)
    #print driver.current_url

def delay_get_spoof(driver, url):
    spoof_click(driver)
    delay = round(random.uniform(3, 5), 2)
    print "Delay %.2f after get(): %s" % (delay, url)
    driver.get(url)
    sleep(delay)
    #print driver.current_url

def delay_click(element):
    delay1 = round(random.uniform(1.5, 1), 2)
    delay2 = round(random.uniform(3, 5), 2)
    text = element.text
    if text == "":
        text = element.get_attribute("value")
        if text == "":
            text = element.get_attribute("name")
            if text == "":
                text = element.get_attribute("id")

    print "Click with delay %.2f %.2f: %s" % (delay1, delay2, text)
    sleep(delay1)
    element.click()
    sleep(delay2)
 

def run():
    if not DEBUG:
        global display 
        display = Display(visible=0, size=(800, 1600))  # extend the display to make more items accessible
        display.start()

    # download json credential file without ask
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', FOLDER)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')

    global driver
    driver = webdriver.Firefox(profile)

    url_console = "https://console.developers.google.com/project"
    url_googlelogin = "https://accounts.google.com/ServiceLogin?continue=" + quote_plus(url_console)

    delay_get(driver, url_googlelogin)

    # login
    delay_send_keys(driver.find_element_by_id("Email"), USER)
    delay_send_keys(driver.find_element_by_id("Passwd"), PASSWORD)
    delay_click(driver.find_element_by_id("signIn"))

    if url_console != driver.current_url:
        raise Exception("Login failed")
    else:
        print "Done: login"

    try:
        print "Trying: no-projects-create"
        delay_click(driver.find_element_by_id("no-projects-create"))
        delay_click(driver.find_element_by_css_selector("span[id=\"tos-agree\"]"))
    except:
        pass
        try:
            print "Trying: projects-create"
            delay_click(driver.find_element_by_id("projects-create"))
        except:
            raise Exception("Both no-projects-create and projects-create failed")

    delay_send_keys(driver.find_element_by_name("name"), PROJECT)
    delay_click(driver.find_element_by_name("ok"))

    print "Creating project with name: %s" % PROJECT
    new_project_id = create_project(driver)

    # page consent
    url_project = url_console + "/" + new_project_id + "/apiui/consent"
    delay_get_spoof(driver, url_project)

    # email
    delay_click(driver.find_element_by_css_selector('div[class="goog-inline-block goog-flat-menu-button-caption"]'))
    delay_click(driver.find_element_by_class_name("goog-menuitem"))

    # product name
    delay_send_keys(driver.find_element_by_name("displayName"), "application")
    delay_click(driver.find_element_by_id("api-consent-save"))

    print "Done: consent"

    # page credential
    url_credential = url_console + "/" + new_project_id + "/apiui/credential"
    delay_get_spoof(driver, url_credential)

    # Create new Client ID
    delay_click(driver.find_element_by_css_selector('jfk-button[jfk-button-style="PRIMARY"]'))

    # Installed application
    txt_application = "Installed application"
    label_application = driver.find_elements_by_css_selector('label')[2]
    if txt_application in label_application.text:
        delay_click(label_application)
    else:
        raise Exception("lable not found: %s" % txt_application)

    # Other
    txt_other = "Other"
    label_other = driver.find_elements_by_css_selector('label')[7]
    if txt_other in label_other.text:
        delay_click(label_other)
    else:
        raise Exception("lable not found: %s" % txt_other)

    # OK
    delay_click(driver.find_element_by_name("ok"))

    print "Done: credential"

    # json URL
    url_downloadjson = driver.find_element_by_css_selector('a[class="goog-inline-block jfk-button jfk-button-standard ng-scope"]').get_attribute("href")
    print "Downloading: %s" % url_downloadjson
    # get json file
    delay_get_spoof(driver, url_downloadjson)

    s = re.search(r'clientId=([^&]+)', url_downloadjson, flags=re.I)
    client_id = s.group(1)
    credential_file = os.path.join(FOLDER, "client_secret_"+client_id+".json")
    f = open(credential_file, 'rb')
    if client_id in f.read():
        # rename 
        new_name = os.path.join(FOLDER, USER+"_"+new_project_id+".json")
        if os.path.isfile(new_name):
            os.remove(new_name)

        os.rename(credential_file, new_name)
        print "Done: credential json file: %s" % new_name

    else:
        raise Exception("Error: credential file invalid: %s" % credential_file)


def unload():
    print "Done: unloading webdriver and virtualdisplay"
    if not DEBUG:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    try:
        run()
    finally:
        unload()
