from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
from seleniumwire import webdriver
from fake_useragent import UserAgent
import time
import os
import json
#The following are from my classes
from skiptracingAddressV1 import skipTraceAddress
from skiptracingdb import db
'''
Description:
    This class is used to webscrape a list of addresses
    Webscraping is done on addressList from [startIndex, endIndex)
'''
class skipTraceList():
    def __init__(self, driver, addressList, argsList, lock):
        self.driver = driver
        self.addressList = addressList
        self.argsList = argsList
        self.lock = lock
    
    def saveProcessState(self):
        data = {}
        if os.path.exists('processData.json'): #is there already data in the file
            with self.lock:
                with open('processData.json', 'r') as fp:
                    data = json.load(fp) 
        
        key = self.argsList[3]
        data[key] = self.argsList
        
        with self.lock:
            with open('processData.json', 'w') as fp:
                json.dump(data, fp)     
                
    #Clicks accept cookies at the start of the driver
    def confirm_cookie(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cc-compliance"))).click()
    
    '''
    Description:
        Starts the web scraping process from the list provided
    Return Values:
        1) tuple (currentIndex, endIndex)
            We only return a tuple if the program stops working
            We return these values because we still plan on skip tracing from the place we 
            left off after the problem is fixed
        2) True
            We successfully skip traced the list
    '''
    def run(self):
        database = db() #associate with database
        self.confirm_cookie()
        time.sleep(1)

        for i in range(self.argsList[0], self.argsList[1]): 
            house = self.addressList[i]
            
            #Extract info from house to make it more readable
            address = house[0]
            city = house[1]
            state = house[2]
            ownerFirstName = house[3]
            ownerLastName = house[4]
            skiptrace1 = skipTraceAddress(self.driver, ownerFirstName, ownerLastName, address, city, state)
            try:
                phoneNumber1 = skiptrace1.startSkipTrace()
                database.importContact(ownerFirstName, ownerLastName, address, city, state, phoneNumber1)
                self.argsList[0] = self.argsList[0] + 1 #resize list
                self.saveProcessState()
            except:
                return False
        return True            
