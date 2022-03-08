from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
from seleniumwire import webdriver
from fake_useragent import UserAgent
import re
import time
import sys 

'''
Description:
    skip traces phone number for one property address
Attributes:
    check constructor, they are all created there
Possible Exceptions:
    timeouterrors
    All exceptions are not caught
'''
class skipTraceAddress():

    def __init__(self, driver, firstName, lastName, address, city, state):
        self.driver = driver
        self.firstName = firstName
        self.lastName = lastName
        self.address = address
        self.city = city
        self.state = state

    #Note: Interacting with the captcha will mutate the DOM and mark the page as having changed => Selenium error stale element
    def areWordsPresentInBody(self, words): 
        wait = WebDriverWait(self.driver, 5)
        while True:
            try:
                pageText = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))).text
                break
            except:
                pass
        areWordsPresent = re.search(words.lower(), pageText.lower())
        if areWordsPresent:
            return True
        return False
    
    def removeCaptcha(self):
        while True:
            iscaptchaPresent1 = self.areWordsPresentInBody("sorry for")
            iscaptchaPresent2 = self.areWordsPresentInBody("please verify you are a human, thanks")
            if iscaptchaPresent1 or iscaptchaPresent2:
                pass
            else:
                break

    def areThereMoreNames(self):
        self.removeCaptcha()
        NoNames = "We could not find any records for that search criteria."
        return not self.areWordsPresentInBody(NoNames)
        
    def minimizePopUpAd(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ee"))).click()
        self.driver.switch_to.default_content()
    
    '''
    (Step 1)
    Description:
        Enters in property Address as a query string into the url
    '''
    def enteringPropertyInfo(self, page):
        searchAddress = self.address.replace("#", "")
        queryString = f"?streetaddress={searchAddress}&citystatezip={self.city},{self.state}&page={page}"
        self.driver.get("https://www.truepeoplesearch.com/resultaddress" + queryString)
    
    '''
    (Step 2)
    Description:
        Checks current page for firstName and lastName that were passed into parameters.
        If the first + last name is found we click on the name that was matched and return true
        Else we stay on the current page stay on the current page and return false
    Return Values:
        Either True or False 
            True (Match was found)
            False (Match was not found)
    Possible Exceptions:
        Timeout exception, if the page takes more than 10 seconds to load
    '''
    def findingName(self): 
        self.removeCaptcha()

        wait = WebDriverWait(self.driver, 10)
        #Note: personList is clickable
        personList = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='card card-body shadow-form card-summary pt-3']")))
        #Not: person is not clickable (it is used for regex matching)
        person = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='card card-body shadow-form card-summary pt-3']//div[@class='h4']")))
        
        for i in range(len(person)):
            #Check firstName lastName
            result1 = re.search(rf"{self.firstName} {self.lastName}", person[i].text)
            #check firstName arbitraryMiddleName lastName
            result2 = re.search(rf"{self.firstName} [a-zA-Z]* {self.lastName}", person[i].text)
            
            if(result1 or result2):
                print("Name Found: \t\t" + person[i].text)
                print("Name Requested: \t\t" + self.firstName + " " + self.lastName)
                
                try:
                    personList[i].click()
                except: #A pop up ad likely occured
                    self.minimizePopUpAd()
                    time.sleep(2)
                    personList[i].click()
                return True     
        return False
    
    '''
    (Step 3)
    Description:
        Search the current page for phone Numbers and return a string containing the phone numbers
    Return Values:
        1)Str
            All phone numbers on the current page
            If there are no numbers return the string "####" 
    Possible Exceptions:
        Timeout exception, if the page takes more than 10 seconds to load
    '''
    def findingPhoneNumber(self):
        self.removeCaptcha()
        numList = []
        start = time.time()
        try:
            #Extracting phoneNumbers from page
            wait = WebDriverWait(self.driver, 5)
            phoneNumList = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='row pl-md-3'][2]//div[@class='row pl-sm-2']")))
        except Exception as e: 
            #There was no phoneNumber on the pagee
            return "####"

        for phoneNum in phoneNumList:
            numList.append(phoneNum.text)

        #Parse each element in numList for only numbers
        numListString = ""
        for num in numList:
            result = re.search(r"\(\d\d\d\) \d\d\d-\d\d\d\d - [a-zA-Z]*", num)
            if result:
                numListString += num + " "
        
        #Check if no numbers were found 
        if numListString == "":
            return "####"
        return numListString 
    '''
    Description:
        Puts all the other functions together into one, skip traces address passed in constructor
    Return Values: 
        1)str 
            Phone Number (Meaning address was skip traced successfully)
            NoName (Meaning name linked to address was not found)
            #### (Meaning name linked to address was found but did not contain a number)
    '''
    def startSkipTrace(self):
        page=1
        number = "NoName" #This is the defualt
        self.enteringPropertyInfo(page)
        while self.areThereMoreNames():
            time.sleep(randint(6,9))
            if self.findingName(): #Name was found on current page
                number = self.findingPhoneNumber()
                time.sleep(randint(6,9))
                break
            else: #Name was not found on current page
                page += 1
            self.enteringPropertyInfo(page)
        return number
        
