from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from user import USER, PASSWORD

url_googlelogin = "https://accounts.google.com/ServiceLogin"
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
    )

driver = webdriver.PhantomJS(desired_capabilities=dcap)
driver.get(url_googlelogin)

driver.find_element_by_id("Email").send_keys(USER)
driver.find_element_by_id("Passwd").send_keys(PASSWORD)                                                            
driver.find_element_by_id("signIn").click()    
print driver.current_url
driver.quit()
