from hashlib import new
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import multiprocessing
import json 
from fake_useragent import UserAgent
import concurrent.futures
import time
import uuid
import os.path
#The following are from my classes
from skiptracingList import skipTraceList
from skiptracingdb import db
from UndetectableDriverV1 import workingDriver

'''
Description:
    A class used to scrap phone numbers from truepeoplesearch.com for a every property in a list of property addresses
    Total Scraps per hour: 475 requests or about 158 properties skip traced per hour
Note:
    The user agent seems to be getting detected which is causing problems with scraping
    Combination:
        Change user agent till it works
        Change proxy till it works
Attribures:
    skipTracesRemaining
        list with everything that we need to skip trace
    proxyList
        list of free proxies available for use
    numberOfProcesses
        number of drivers we are going to have running at once
'''

class skipTraceAll():     
    def __init__(self, proxyList):
        database = db() 
        self.skipTracesRemaining  = database.getSkipTracingList()
        self.numberOfProcesses = len(proxyList)
        self.proxyList = proxyList
    
    '''
    Description:
        Takes our skip tracing list and partitions it so that each process gets a equal amount
    Return Values:
        1)List
            each element is a list containing a [startIndex, endIndex)
    '''
    def getPartitionSizes(self):
        size = len(self.skipTracesRemaining)
        skip = int(size / self.numberOfProcesses)
        remainder = int(size % self.numberOfProcesses)

        #get parition sizes
        partitions = []
        currentIndex = 0
        while currentIndex != size:
            startIndex = currentIndex
            endIndex = startIndex + skip
            if remainder != 0:
                endIndex += 1
                remainder -= 1
            currentIndex = endIndex
            partitions.append([startIndex, endIndex])
        return partitions
    
    '''
    Descriptions:
        adds a proxy into each partition, i.e assigns a proxy to each partition
    Return values:
        1) List
            each element is a list containing a startIndex, endIndex, and a proxy
    '''
    def assignProxies2Partitions(self):
        partitionSizes = self.getPartitionSizes()
        for part,prox in zip(partitionSizes, self.proxyList):
            part.append(prox)
            part.append(str(uuid.uuid4()))
        return partitionSizes

    '''
    Description:
        prints a list of all the processes and their arguments
    '''
    def printProcesses(self, args):
        for i in range(len(args)):
            print("Process: ", i, " ; Arguments: ", args[i])

    def saveProcessState(self, argsList, lock):
        data = {}
        if os.path.exists('processData.json'): #is there already data in the file
            with lock:
                with open('processData.json', 'r') as fp:
                    data = json.load(fp) 
        
        key = argsList[3]
        data[key] = argsList
        
        with lock:
            with open('processData.json', 'w') as fp:
                json.dump(data, fp)     
        
    def getProcessState(self, argsList, lock):
        data = {}
        if os.path.exists('processData.json'):
            with lock:
                with open('processData.json', 'r') as fp:
                    data = json.load(fp)
        key = argsList[3]
        return data[key]

    def deleteProcessState(self, argsList, lock):
        data = {}
        if os.path.exists('processData.json'): #is there already data in the file
            with lock:
                with open('processData.json', 'r') as fp:
                    data = json.load(fp) 
        
        key = argsList[3]
        del data[key] 

        with lock:
            with open('processData.json', 'w') as fp:
                json.dump(data, fp)     

    '''
    Description:
        This sets up all of our processes and puts everything together
    '''
    def startProcesses(self):
        if os.path.exists('processData.json'): #is there already data in the file
            os.remove('processData.json')

        args = self.assignProxies2Partitions()
        
        print("\nInitial Processes")
        self.printProcesses(args)
        print("")
        
        m = multiprocessing.Manager()
        lock = m.Lock()

        #start processes
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = {executor.submit(self.skipTracePartition, i, lock): i for i in args}
            while len(results.keys()) != 0:
                for future in concurrent.futures.as_completed(results.keys()):
                    if future.exception() is not None: #Some exception occured, Restart Process
                        print("Process generated an exception: ", future.exception())
                        newArgs = self.getProcessState(results[future], lock)
                        del results[future]
                        results[executor.submit(self.skipTracePartition, newArgs, lock)] = newArgs
                    else: #No exception occured
                        if future.result(): #process completed correctly (return was = True)
                            print("Process completed successfully")
                            self.deleteProcessState(results[future], lock)
                            del results[future]
                        else: #process did not complete correctly, restart Process
                            print("Process error, process restarting")
                            newArgs = self.getProcessState(results[future], lock)
                            del results[future]
                            results[executor.submit(self.skipTracePartition, newArgs, lock)] = newArgs
                    break
        print("!!!Everything finished correctly!!!")

    '''
    Description:
        Sets up working driver, and skip traces a portion of the list
    Parameters:
        argsList: List
            [0] = StartIndex of the portion of the list that we want to skip trace
            [1] = EndIndex of the portion of the list that we want to skip trace
            [2] = The proxy that we are going to use
            [3] = Guid to identify the process that is running
    '''
    def skipTracePartition(self, argsList, lock):
        #Make Driver with the given proxy and a random user agent    
        proxy = argsList[2]      
        driverObj = workingDriver(proxy)
        driver = driverObj.getWorkingDriver()

        if driver: #page works
            obj = skipTraceList(driver,self.skipTracesRemaining, argsList, lock)
            time.sleep(3)
            result = obj.run()
            driver.quit()
            return result
        else: #Page doesnt work
            return False
