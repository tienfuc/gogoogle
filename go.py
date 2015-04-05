from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from user import USER, PASSWORD, PROJECT

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
    )
display = Display(visible=0, size=(800, 600))
display.start()
 
#driver = webdriver.PhantomJS(desired_capabilities=dcap)
#driver = webdriver.Firefox()
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

url_googlelogin = "https://accounts.google.com/"
driver.get(url_googlelogin)

driver.find_element_by_id("Email").send_keys(USER)
driver.find_element_by_id("Passwd").send_keys(PASSWORD)                                                            
driver.find_element_by_id("signIn").click()    

print driver.current_url

url_login_ok = "https://myaccount.google.com/?pli=1"
url_login_bad = "https://accounts.google.com/ServiceLoginAuth"

if driver.current_url != url_login_ok:
    raise Exception("Login failed")
else:
    print "Login ok"

url_console = "https://console.developers.google.com/project"
driver.get(url_console)

project_name = "application-0001"
from time import sleep

sleep(3)
driver.find_element_by_id("projects-create").click()
driver.find_element_by_name("name").send_keys(PROJECT)
sleep(3)
driver.find_element_by_name("ok").click()

driver.quit()
display.stop()
