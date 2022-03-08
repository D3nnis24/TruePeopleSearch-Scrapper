from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from seleniumwire import webdriver
import undetected_chromedriver.v2 as uc
import time
import re
import time
'''
Attributes:
    userAgent
    proxy
'''
class workingDriver():
    def __init__(self, proxy=None):
        self.proxy = proxy  

    def areWordsPresentInBody(self, driver, words): 
        wait = WebDriverWait(driver, 10)
        pageText = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text.lower()
        words = words.lower()
        areWordsPresent = re.search(words, pageText)
        if areWordsPresent:
            return True
        return False
    
    def pageLoadedCorrectly(self, driver):
        driver.get("https://www.truepeoplesearch.com")
        #check for cloudflare error
        error1 = self.areWordsPresentInBody(driver, "error") 
        error2 = self.areWordsPresentInBody(driver, "we are checking your browser")
        #check for captcha error
        error3 = self.areWordsPresentInBody(driver, "sorry for")
        error4 = self.areWordsPresentInBody(driver, "please verify you are a human, thanks.")
        error5 = self.areWordsPresentInBody(driver,"captcha")
        if error1 or error2 or error3 or error4 or error5:
            return False
        return True
  
    def changeUserAgent(self, driver):
        #Get a random user agent
        ua = UserAgent()
        userAgent = ua.random
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": userAgent})

    def saveCurrentUserAgent(self, driver, file="userAgentFile.txt"):
         #save working user agent to it
            user_agent = driver.execute_script("return navigator.userAgent;")
            with open("userAgentFile.txt", "a") as f:
                f.write(user_agent)
                f.write("\n")
    
    def makeDriverMethod1(self):
        options = webdriver.ChromeOptions() 

        #Add arguments to prevent easy bot detection
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        prefs = {"enable_do_not_track": True}
        options.add_experimental_option("prefs", prefs)

        #setting userAgent
        ua = UserAgent()
        userAgent = ua.random
        options.add_argument(f"user-agent={userAgent}")

        #setting proxy up
        if self.proxy: #proxy is used
            options2 =  {
                "verify_ssl": False,
                'mitm_http2': False,
                'proxy': {
                    'http': 'http://' + self.proxy,
                    'https': 'https://' + self.proxy,
                    'no_proxy': 'localhost,127.0.0.1' # excludes
                }
            }
            driver = webdriver.Chrome("C:\webdrivers\chromedriver.exe", seleniumwire_options=options2, options=options)
        else: #proxy not used   
            options.add_argument("user-agent=Opera/9.80 (X11; Linux i686; U; it) Presto/2.7.62 Version/11.00")
            driver = webdriver.Chrome("C:\webdrivers\chromedriver.exe", options=options)

        #Execution on driver to prevent detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(20)
        return driver   
    
    def makeDriverMethod2(self):
        options = uc.ChromeOptions()

        # setting profile
        options.user_data_dir = "c:\\temp\\profile"

        # another way to set profile is the below (which takes precedence if both variants are used
        options.add_argument('--user-data-dir=c:\\temp\\profile2')

        # just some options passing in to skip annoying popups
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        driver = uc.Chrome(options=options)
        return driver

    def getWorkingDriver(self):    
        startTime = time.time()
        while True:
            driver = self.makeDriverMethod1()
            if self.pageLoadedCorrectly(driver): #driver was undetected
                self.saveCurrentUserAgent(driver)
                return driver #return the working driver
            elif time.time() - startTime >= 60: #elapsed time has been too long
                driver.quit()
                return False
            driver.quit()
