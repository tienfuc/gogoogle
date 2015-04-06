from pyvirtualdisplay import Display
from selenium import webdriver
from urllib import quote_plus
import re, os
from time import sleep

from user import USER, PASSWORD, PROJECT, FOLDER

import sys
#from IPython.core import ultratb
#sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)

display = Display(visible=0, size=(800, 600))
display.start()

# download json credential file without ask
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', FOLDER)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')

driver = webdriver.Firefox(profile)

url_console = "https://console.developers.google.com/project"
url_googlelogin = "https://accounts.google.com/ServiceLogin?continue=" + quote_plus(url_console)

driver.get(url_googlelogin)

# login
driver.find_element_by_id("Email").send_keys(USER)
driver.find_element_by_id("Passwd").send_keys(PASSWORD)                                                            
driver.find_element_by_id("signIn").click()    

if url_console != driver.current_url:
    raise Exception("Login failed")
else:
    print "Login ok"

sleep(3)
driver.find_element_by_id("projects-create").click()
driver.find_element_by_name("name").send_keys(PROJECT)
sleep(3)
driver.find_element_by_name("ok").click()
print "creating project: %s" % PROJECT
# wait for project creation
sleep(30)

print "project creation done: %s" % PROJECT

application_name = driver.find_element_by_css_selector("b[class=\"ng-binding\"]").text

# page consent
url_project = url_console + "/" + PROJECT + "/apiui/consent"
driver.get(url_project)
sleep(3)

# email
driver.find_element_by_css_selector('div[class="goog-inline-block goog-flat-menu-button-caption"]').click()
driver.find_element_by_class_name("goog-menuitem").click()

# product name
driver.find_element_by_name("displayName").send_keys("application")
driver.find_element_by_id("api-consent-save").click()

print "consent ok"

# page credential
url_credential = url_console + "/" + PROJECT + "/apiui/credential"
driver.get(url_credential)
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
credential_file = os.path.join(FOLDER, "client_secret_"+s.group(1)+".json")

print "Credential json file: %s" % credential_file

driver.quit()
display.stop()
