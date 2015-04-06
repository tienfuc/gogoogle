from pyvirtualdisplay import Display
from selenium import webdriver
from urllib import quote_plus
import re, os
from time import sleep

from user import USER, PASSWORD, PROJECT, FOLDER

import sys

VIRTUAL_DISPLAY=0

def create_project(driver):
    # wait for project creation
    max_retries = 30
    while True:
        sleep(1)
        try:
            application_name = driver.find_element_by_css_selector("b[class=\"ng-binding\"]").text
            if application_name:
                print "Project creation done: %s" % application_name
                return application_name
        except:
            pass

        max_retries -= 1
        if max_retries < 0:
            raise Exception("Project creation failed: %s" % PROJECT)

def run():
    if VIRTUAL_DISPLAY:
        global display 
        display = Display(visible=0, size=(800, 600))
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

    driver.get(url_googlelogin)
    print driver.current_url
    sleep(2)

    # login
    driver.find_element_by_id("Email").send_keys(USER)
    driver.find_element_by_id("Passwd").send_keys(PASSWORD)                                                            
    driver.find_element_by_id("signIn").click()    
    sleep(8)

    if url_console != driver.current_url:
        print "Login failed"
        return
    else:
        print "Login ok"

    projects = driver.find_elements_by_css_selector("a[class=\"p6n-clickable-link ng-binding ng-scope\"]")
    
    try:
        print "no-projects-create"
        driver.find_element_by_id("no-projects-create").click()
        driver.find_element_by_css_selector("span[id=\"tos-agree\"]").click()
    except:
        pass
        try:
            print "projects-create"
            driver.find_element_by_id("projects-create").click()
        except:
            raise Exception("Both no-projects-create and projects-create failed")

    driver.find_element_by_name("name").send_keys(PROJECT)
    sleep(2)
    driver.find_element_by_name("ok").click()
    print "Creating project: %s" % PROJECT
    new_project_name = create_project(driver)

    # page consent
    url_project = url_console + "/" + new_project_name + "/apiui/consent"
    driver.get(url_project)
    print driver.current_url
    sleep(3)

    # email
    driver.find_element_by_css_selector('div[class="goog-inline-block goog-flat-menu-button-caption"]').click()
    driver.find_element_by_class_name("goog-menuitem").click()

    # product name
    driver.find_element_by_name("displayName").send_keys("application")
    driver.find_element_by_id("api-consent-save").click()
    sleep(2)

    print "consent ok"

    # page credential
    url_credential = url_console + "/" + new_project_name + "/apiui/credential"
    driver.get(url_credential)
    print driver.current_url
    sleep(5)

    # Create new Client ID
    driver.find_element_by_css_selector('jfk-button[jfk-button-style="PRIMARY"]').click()
    sleep(3)

    # Installed application
    txt_application = "Installed application"
    label_application = driver.find_elements_by_css_selector('label')[2]
    if txt_application in label_application.text:
        label_application.click()
    else:
        raise Exception("lable not found: %s" % txt_application)

    # Other
    txt_other = "Other"
    label_other = driver.find_elements_by_css_selector('label')[7]
    if txt_other in label_other.text:
        label_other.click()
    else:
        raise Exception("lable not found: %s" % txt_other)

    # OK
    driver.find_element_by_name("ok").click()

    print "credential ok"

    sleep(3)

    # json URL
    url_downloadjson = driver.find_element_by_css_selector('a[class="goog-inline-block jfk-button jfk-button-standard ng-scope"]').get_attribute("href")
    print "Downloading: %s" % url_downloadjson
    # get json file
    driver.get(url_downloadjson)

    s = re.search(r'clientId=([^&]+)', url_downloadjson, flags=re.I)
    client_id = s.group(1)
    credential_file = os.path.join(FOLDER, "client_secret_"+client_id+".json")
    f = open(credential_file, 'rb')
    if client_id in f.read():
        # rename 
        new_name = os.path.join(FOLDER, USER+"_"+new_project_name+".json")
        if os.path.isfile(new_name):
            os.remove(new_name)

        os.rename(credential_file, new_name)
        print "Credential json file: %s" % new_name

    else:
        raise Exception("Credential json file is invalid: %s" % credential_file)


def unload():
    print "Unloading webdriver and virtualdisplay"
    driver.quit()
    if VIRTUAL_DISPLAY:
        display.stop()

if __name__ == "__main__":
    try:
        run()
    finally:
        unload()
