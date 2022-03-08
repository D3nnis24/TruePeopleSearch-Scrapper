import sqlite3
import os.path
#This class will interact with our database
class db():
    def __init__(self, database="records.db"):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(BASE_DIR, database)
    '''
    Description:
        Connects to records.db and imports a record into contacts table, if the lock cant be grabbed within 15 seconds we get a timeout error
    Parameters:
        firstName: str
        lastName: str
        Address: str
        City: str
        State: str
        PhoneNumbers: str
            If PhoneNumbers == "####" this means owner name was found but phone number was unavailable
            If PhoneNumbers == "NoName" this means that the owner name could not be found
    ''' 
    def importContact(self, firstName, LastName, Address, City, State, PhoneNumbers):  
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            c = conn.cursor()
            contact = (firstName,LastName,Address,City,State,PhoneNumbers)
            print(f"\n{contact}\n")
            sql = ''' INSERT INTO contacts(FirstName,LastName,PropertyAddress,PropertyCity,PropertyState,PhoneNumbers)
                VALUES(?,?,?,?,?,?) '''
            c.execute(sql, contact)
            conn.commit()
            conn.close()
    '''
    Description:
        Connects to records.db, examines properties and contacts table, retrieves list of properties 
        that have not been skip traced and returns them 
    Return Values:
        1)List 
            Each element in the list corresponds to a property.
            Element format:
                Ex) List[0] = [Address, City, State, OwnerFirstName, OwnerLastName]       
    '''
    def getSkipTracingList(self):   
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM remainingOwner1")
        skiptraceRemaining = cursor.fetchall()
        cursor.execute("SELECT * FROM remainingOwner2")
        skiptraceRemaining = skiptraceRemaining + cursor.fetchall()
        conn.close()
        return skiptraceRemaining

        
    
