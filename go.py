from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from urllib import quote_plus
import re, os, random
from time import sleep

from user import USER, PASSWORD, PROJECT, FOLDER, DEBUG, PHONE_NUMBER

import sys



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
    delay1 = round(random.uniform(1, 2), 2)
    print "Delay %.2f after send_keys(): %s" % (delay1, keys)
    for k in list(keys):
        delay2 = round(random.uniform(0, 0.2), 2)
        sleep(delay2)
        element.send_keys(k)
    sleep(delay1)


def spoof_click(driver):
    total = random.randint(2,6)
    count = 1

    for i in range(0, total):
        items = driver.find_elements_by_xpath("//dt[contains(@class, \"p6n-tree-node ng-scope ng-isolate-scope\")]/div/div/div/a/span[@class=\"ng-binding\"]/..")
        for item in random.sample(items, 1):
            attr = ""
            try:
                attr = item.get_attribute("pan-nav-tooltip") or item.get_attribute("title")
            except:
                 print "Error: failed to get pan-nav-tooltip or title"
                 pass
            else:
                delay1 = round(random.uniform(0.3, 1), 2)
                delay2 = round(random.uniform(0.3, 1), 2)
                try: 
                    span = item.find_element_by_xpath("span")
                except:
                    print "Error: failed to get span"
                    pass
                else:
                    if not span.is_displayed():
                        try:
                            top = item.find_element_by_xpath("../../../../../../../preceding-sibling::*[1]")
                            print "Delay %.2f after spoof top click: %s" % (delay1, top.text)
                            if top.is_displayed():
                                sleep(delay1)
                                top.click()
                        except:
                            print "Error: failed to find preceding-sibling and click"
                            pass

                    if span.is_displayed():
                        print "Delay %.2f after spoof click (%d of %d): %s" % (delay2, count, total, attr)
                        count += 1
                        sleep(delay2)
                        try:
                            span.click()
                        except:
                            print "Error: failed to click span"
                            pass
                    
    return


def delay_get(driver, url):
    delay = round(random.uniform(3, 5), 2)
    print "Delay %.2f after get(): %s" % (delay, url)
    driver.get(url)
    sleep(delay)


def delay_get_spoof(driver, url):
    spoof_click(driver)
    delay = round(random.uniform(3, 5), 2)
    print "Delay %.2f after get(): %s" % (delay, url)
    driver.get(url)
    sleep(delay)


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
 

def enable_api(driver, project_id, api):
    base_url = "https://console.developers.google.com/project/%s/apiui/apiview/%s/overview"
    for a in api:
        url = base_url % (project_id, a)
        delay_get_spoof(driver, url)
        span = driver.find_element_by_xpath("//span[@class=\"p6n-loading-button-regular-text\"]")
        print "Enable API: %s" % a
        span.click()


def pass_phone_check1(driver):
    # radio 
    print "pass_phone_check1"
    radio = driver.find_element_by_xpath("//input[@id=\"PhoneVerificationChallenge\"]")
    radio.click()
    phone_number = driver.find_element_by_xpath("//input[@id=\"phoneNumber\"]")
    phone_number.send_keys(PHONE_NUMBER)
    submit = driver.find_element_by_xpath("//input[@id=\"submitChallenge\"]")
    submit.click()


def pass_phone_check2(driver):
    print "pass_phone_check2"
    submit = driver.find_element_by_xpath("//input[@id=\"save\"]")
    submit.click()


def run():
    if not DEBUG:
        global display 
        display = Display(visible=0, size=(800, 3200))  # extend the display to make more items accessible
        display.start()

    # download json credential file without ask
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', FOLDER)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')

    global driver
    driver = webdriver.Firefox(profile)
    driver.maximize_window()

    url_console = "https://console.developers.google.com/project"
    url_googlelogin = "https://accounts.google.com/ServiceLogin?continue=" + quote_plus(url_console)

    delay_get(driver, url_googlelogin)

    # login
    delay_send_keys(driver.find_element_by_id("Email"), USER)
    delay_send_keys(driver.find_element_by_id("Passwd"), PASSWORD)
    delay_click(driver.find_element_by_id("signIn"))

    # phone number check
    try:
        pass_phone_check1(driver)
    except:
        pass

    try:
        pass_phone_check2(driver)
    except:
        pass

    if url_console != driver.current_url:
        raise Exception("Login failed")
    else:
        print "Done: login"

    try:
        print "Trying: no-projects-create"
        delay_click(driver.find_element_by_id("no-projects-create"))
    except:
        pass
        try:
            print "Trying: projects-create"
            delay_click(driver.find_element_by_id("projects-create"))
        except:
            raise Exception("Both no-projects-create and projects-create failed")

    #delay_click(driver.find_element_by_css_selector("span[id=\"tos-agree\"]"))
    try:
        agree = driver.find_element_by_css_selector("span[id=\"tos-agree\"]")
    except:
        pass
    else:
        delay_click(agree)

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

    # get json file
    delay_get_spoof(driver, url_downloadjson)

    s = re.search(r'clientId=([^&]+)', url_downloadjson, flags=re.I)
    client_id = s.group(1)
    credential_file = os.path.join(FOLDER, "client_secret_"+client_id+".json")
    f = open(credential_file, 'rb')
    if client_id in f.read():
        # rename 
        new_name = os.path.join(FOLDER, USER+"="+new_project_id+".json")
        if os.path.isfile(new_name):
            os.remove(new_name)

        os.rename(credential_file, new_name)
        print "Done: credential json file: %s" % new_name

    else:
        raise Exception("Error: credential file invalid: %s" % credential_file)

    apis = ["drive", "fusiontables"]
    enable_api(driver, new_project_id, apis)

    return 0

def unload():
    print "Done: unloading webdriver and virtualdisplay"
    if not DEBUG:
        driver.quit()
        display.stop()

if __name__ == "__main__":
    try:
        result = run()
    except:
        result = 1   
        driver.get_screenshot_as_file("/tmp/webdriver_screenshot.png")
        with open("/tmp/webdriver_source.html", "wb") as f:
            f.write(driver.page_source.encode('utf-8'))
        raise
    finally:
        unload()
    
    sys.exit(result)
