import encryption
import json

admins = {} # key = admin id, password = password
patients = {} # key = phone, password = password

def readCredentials():
    with open("credentials/patients.txt", "r") as f:
        content = f.readlines()
    
    patients = dict([x.strip().split(",") for x in content])
    with open("credentials/admins.txt", "r") as f:
        content = f.readlines()
        
    admins = dict([x.strip().split(",") for x  in content])

    return patients, admins
def getRole()->str:
    role = input("A for Admin\nP for Patient\nEnter Role: ")
    if role.lower() == "a":
        return "a"
    elif role.lower() == "p":
        return "p"
    else:
        print("Enter a valid response please!")
        return getRole()
        
def admin_login(admins:dict):
    login_id=input("Enter login id:")
    login_pass=input("Enter password:")
    while " " in login_id or " " in login_pass:
        print("Space not included")
        login_id=input("Enter login id:")
        login_pass=input("Enter password:")
    if(login_id not in list(admins.keys())):
        print("Enter a valid login ID...")
        admin_login(admins)
    if(login_pass!=admins[login_id]):
        print("Enter valid password...")
        admin_login(admins)
    print("logged in successfully...")
    option=input("Enter 1- for update \n 2- for view data")
    while option not in ["1","2"]:
        print("Enter valid input")
        option=input("Enter 1- for update \n 2- for view data")    
    if(option=="1"):
        phone = ""
        while phone == "":
            phone = input("Enter phone number of the person who's record you want to change: ")
            if len(phone) < 10:
                print("Invalid Phone number!")
                phone = ""
                continue
            phone = phone[-10:]
            if phone.isnumeric() == False:
                phone = ""
                print("Invalid phone number!")
                continue
            break
        key = input("Enter encryption key: ")
        encryption.update_data(key.encode(encoding = 'utf-8'), phone)

    else:
        
        with open("keymap.txt", "r") as f:
            content = f.readlines()
        content = [x.strip().split(",") for x in content]   #[[line 1],[]]
        key=""
        while(key==""):
            phone=input("Enter Phone number for which the key is to be obtained:")[-10:]
            while " " in phone or phone.isnumeric() == False:
                print("Enter a valid Phone number")
                phone=input("Enter Phone number for which the key is to be obtained:")[-10:]
            record_found = False
            for i in content:
                if phone==i[2]:
                    key=i[3][2:-1].encode(encoding = 'utf-8')
                    print(key)
                    encryption.fetch_data(key, phone)
                    record_found = True
            if not record_found:
                print('no such record found:')
                b=input("do you want to break press 0")
                if b==0:
                    break
       
    return

def admin_signup(admin:dict):
    id=input("Enter admin id (nospace): ")
    password=input("Enter password (nospace): ")
    if id in list(admin.keys()):
        print("Existing admin")
        admin_login(admin)
    while " " in id or " " in password:
        print("Enter a valid id and password (nospace)")
        id=input("Enter admin id")
        password=input("Enter password")
    admin[id]=password
    with open("credentials/admins.txt", "a") as f:
        f.write(f"{id},{password}\n")
    admin_login(admin)

def patient_login()->str:
    phone = input("Enter Phone Number: ")
    if len(phone) < 10:
        print("Invalid Phone Number!")
        patient_login()
    else:
        phone = phone[-10:]
    
    if phone not in patients:
        print("No account associated with the phone number")
        print("Please Sign Up")
        patient_signup()
    password = input("Enter Password: ")

    if patients[phone] != password:
        print("Incorrect Password! Login Again")
        patient_login()
    
    else:
        print("Logged In Successfully")
        
    command = ""
    while command not in ("1", "2"):
        print("Enter 1 - To start a new chat\nEnter 2 - To view a record")
        command = input("Which function do you want to perform: ")

        if command == "1":
            data = encryption.encrypt_data(phone)
            encryption.store_data(data)

            print("Data Successfuly stored!")

        elif command == "2":
            key = input("Enter encryption key: ").encode(encoding = 'utf-8')
            encryption.fetch_data(key, phone)

def patient_signup():
    phone = input("Enter phone number: ")

    if len(phone) < 10:
        print("Enter A valid Phone number!")
        patient_signup()

    phone = phone[-10:]
    if phone.isumeric() == False:
        print("Invalid Phone number!")
        patient_signup()

    if phone in patients:
        print("Account already exists! Please login")
        patient_login()
    
    password = input("Enter password (no spaces): ")

    if " " in password:
        print("Password cannot contain a <space>.\nSignup attempt failed.\nSignup again")
        patient_signup()
    
    else:
        with open("credentials/patients.txt", "a") as f:
            f.write(f"{phone},{password}\n")
        print("Account created successfully! Please sign in.\n")
        patient_login()


def getCredentials(role:str):
    if role == "a":
        # Login: Admin ID, Password... Signup: ADMIN ID, create password
        # View Record or Update
        choice=int(input("Enter 1- for login \n 2- for sign up"))
        while choice!=1 or choice!=2:
            print("enter a valid option:")
            choice=int(input("Enter 1- for login \n 2- for sign up"))
        if choice==1:
            admin_login()

        pass
    if role == "p":
        # View Record or new chat
        pass

patients, admins = readCredentials()
print(patients)
print(admins)
role = getRole()
if role == "p":
    patient_login()
elif role == "a":
    admin_signup(admins)
    