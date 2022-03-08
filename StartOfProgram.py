'''
This application works with proxies from website www.proxycheap.com
'''
from skiptracingAll import *

def main():
    print("###############################")
    print("TRUE PEOPLE SEARCH SKIP TRACING")
    print("###############################")
    
    #Get user input on how to run the application
    numOfProcesses = int(input("Number of processes > "))
    numOfProcessesUsingProxies = int(input("How many of these processes will use proxies > "))
    numOfProcessesUsingLocalHost = numOfProcesses - numOfProcessesUsingProxies

    #Check if we are going to be using a proxy
    if numOfProcessesUsingProxies > 0:
        proxy = input("Enter proxy (username:password@ip:port) > ")

    #Making list (mix of local hosts and proxies) that we are going to be passing as the argument
    proxyList1 = [None for i in range(numOfProcessesUsingLocalHost)]
    proxyList2 = [proxy for i in range(numOfProcessesUsingProxies)]
    proxyList = proxyList1 + proxyList2

    obj = skipTraceAll(proxyList)
    obj.startProcesses()

if __name__ == "__main__":
    main()
