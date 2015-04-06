from pyvirtualdisplay import Display
from selenium import webdriver
from urllib import quote_plus

from user import USER, PASSWORD, PROJECT, FOLDER

display = Display(visible=0, size=(800, 600))
display.start()
 
#driver = webdriver.PhantomJS(desired_capabilities=dcap)
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', FOLDER)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')

driver = webdriver.Firefox(profile)
#driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

url_console = "https://console.developers.google.com/project"
url_googlelogin = "https://accounts.google.com/ServiceLogin?continue=" + quote_plus(url_console)
driver.get(url_googlelogin)

driver.find_element_by_id("Email").send_keys(USER)
driver.find_element_by_id("Passwd").send_keys(PASSWORD)                                                            
driver.find_element_by_id("signIn").click()    

if url_console != driver.current_url:
    raise Exception("Login failed")
else:
    print "Login ok"

from time import sleep

sleep(3)
driver.find_element_by_id("projects-create").click()
driver.find_element_by_name("name").send_keys(PROJECT)
sleep(3)
driver.find_element_by_name("ok").click()

sleep(30)

application_name = driver.find_element_by_css_selector("b[class=\"ng-binding\"]").text

url_project = url_console + "/" + PROJECT + "/apiui/consent"
print url_project

driver.get(url_project)
sleep(3)

# email
driver.find_element_by_css_selector('div[class="goog-inline-block goog-flat-menu-button-caption"]').click()
driver.find_element_by_class_name("goog-menuitem").click()

# product name
driver.find_element_by_name("displayName").send_keys("application")
driver.find_element_by_id("api-consent-save").click()

# Credential
url_credential = url_console + PROJECT + "/apiui/credential"
driver.get(url_credential)
#class="jfk-button goog-inline-block jfk-button-primary"
#driver.find_element_by_css_selector('jfk-button[class="jfk-button goog-inline-block jfk-button-primary jfk-button-clear-outline"]').click()

# Create new Client ID
driver.find_element_by_css_selector('jfk-button[class="jfk-button goog-inline-block jfk-button-primary"]').click()
# Installed application
driver.find_elements_by_css_selector('label')[2].click()
sleep(3)
# Other
#driver.find_elements_by_css_selector('label[class="ng-scope ng-isolate-scope p6n-radio"')[4].click()
driver.find_elements_by_css_selector('label')[7].click()
# OK
driver.find_element_by_name("ok").click()

# json URL
url_downloadjson = driver.find_element_by_css_selector('a[class="goog-inline-block jfk-button jfk-button-standard ng-scope"]').get_attribute("href")

driver.get(url_downloadjson)

#u'https://console.developers.google.com/m/api/clientjson?pid=application-0003&clientId=549709388578-pmbil0dabgfhqt0vtiei1tlhe14hi6o4.apps.googleusercontent.com&authuser=0&xsrf=AFE_nuMQ-DgiWuFcW3X4to5d4rzkAOu2oA:1428297479657'
import re, os
s = re.search(r'clientId=([^&]+)', url_downloadjson, flags=re.I)
credential_file = os.path.join(FOLDER, "client_secret_"+s.group(1)+".json")

print credential_file

driver.quit()
display.stop()
