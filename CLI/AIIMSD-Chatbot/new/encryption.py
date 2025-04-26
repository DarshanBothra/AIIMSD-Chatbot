import report
import pymysql
from cryptography.fernet import Fernet
from datetime import datetime

conn= pymysql.connect(host="localhost",user="root",password="password")
cursor=conn.cursor()


def createTable():
    cursor.execute("show databases")
    db = cursor.fetchall()
    if (("MODULE3", )) not in db:
        cursor.execute("create database MODULE3")
    cursor.execute("use MODULE3")
    cursor.execute("show tables")

    tables = cursor.fetchall()
    print(tables)
    if (("DATA",) not in tables):
        cursor.execute("create table DATA (PHONE VARCHAR(255), NAME LONGBLOB,AGE LONGBLOB,GENDER LONGBLOB,DISEASES LONGBLOB,SYMPTOMS LONGBLOB,FREQUENCY LONGBLOB,DURATION LONGBLOB,SEVERITY LONGBLOB,ORTHOCHECK LONGBLOB)")

def encrypt_data(phone):
    conn = pymysql.connect(host="localhost", user="root", password="password")
    cursor = conn.cursor()
    cursor.execute("use MODULE3")
    enckey = Fernet.generate_key()
    print("key: ",enckey)
    cipher_suite = Fernet(enckey)
    # print("Cipher Suite: ", cipher_suite.__class__.__name__)
    # print()


    data = {
        "phone": "1234567890",
        "name": "Darshan",
        "age": "18",
        "gender": "Male",
        "diseases": "Arthritis, Diabetes",
        "symptoms": "chest pain, back pain, joint pain, pain in arms, fatigue",
        "frequency": "very frequent",
        "start-time": "3 days",
        "severity": 8,
        "orthoCheck": True

    }
    # data = report.main(enckey, phone)  # uncomment this
    encrypted_data = {}
    for key, value in data.items():
        if key == "phone":
            encrypted_data[key] = value
            continue
        encoded_text = cipher_suite.encrypt(bytes(str(value), encoding = 'utf-8'))

        encrypted_data[key] = encoded_text

    for key, value in data.items():
        print(f"{key}: {value}")
    print()

    for key, value in encrypted_data.items():
        print(f"{key}: {value}")
    print()
    dt = str(datetime.now())
    date_temp = dt[:10]
    final_date = ""  # YYYYMMDD
    for char in date_temp:
        if char != "-":
            final_date += char

    time_temp = dt[11:19]
    final_time = ""  # HHMMSS

    for char in time_temp:
        if char != ":":
            final_time += char
    with open("keymap.txt", "a") as f:
        f.write(f"{final_date},{final_time},{data["phone"]},{enckey}\n")
    return encrypted_data


def store_data(data):
    conn = pymysql.connect(host = "localhost", user = "root", password = "password")
    cursor = conn.cursor()
    cursor.execute("use MODULE3")
    query = "insert into DATA values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = tuple(data.values())
    cursor.execute(query, values)
    conn.commit()

def fetch_data(key, phone):
    conn = pymysql.connect(host = "localhost", user = "root", password = "password")
    cursor = conn.cursor()
    cursor.execute("use MODULE3")
    query = 'show columns from DATA'
    cursor.execute(query)
    ans = cursor.fetchall()
    column_names = []
    for column in ans:
        column_names.append(column[0].capitalize())

    cipher_suite = Fernet(key)
    
    query = "select * from DATA where phone = %s"
    values = (phone)
    cursor.execute(query, values)
    records = cursor.fetchall()
    printed = False
    if records:

        # Decode and display Data
        for record  in records:
            patient_record = {}
            try:
                for i in range(len(record)):
                    patient_record[column_names[i]] = f"{record[i] if i == 0 else cipher_suite.decrypt(record[i])}"
                for key, value in patient_record.items():
                    print(f"{key}: {value}")
                print("-"*100)
                printed = True
            except:
                continue
        # decoded_text = cipher_suite.decrypt(encoded_text)
    if records == False or printed == False:
        print("No record associated with this phone-number and encryption code. Check if the phone number and the encryption code are correct")

def update_data(key, phone):

    with open("keymap.txt", "r") as f:
        content = f.readlines()

    content = [x.strip().split(",") for x in content]
    enckey = str(key)
    if enckey.startswith("b'"):
        enckey = enckey[2:]
    if enckey.endswith("'"):
        enckey = enckey[:-1]

    for line in content:
        if line[2] == phone and line[3][2:-1] == enckey:
            break

    else:
        print("No record associated with this key and phone composition")
        return None

    cipher_suite = Fernet(key)

    new_phone = input("Enter new/old number: ")
    if len(new_phone) < 10:
        print("Invalid Phone Number!")
        print("Record updation failed")
        return None
    new_phone = new_phone[-10:]
    if new_phone.isnumeric() == False:
        print("Invalid Phone number!")
        print("record updation failed!")
        return None

    new_name = input("Enter new name: ")
    new_age = input("Enter new age: ")
    if new_age.isnumeric() == False:
        print("Invalid Age")
        print("Record updation failed")
        return None
    new_gender = input("Enter new gender: ")

    try:

        encrypted_name = cipher_suite.encrypt(bytes(new_name, encoding = 'utf-8'))
        encrypted_age = cipher_suite.encrypt(bytes(new_age, encoding = 'utf-8'))
        encrypted_gender = cipher_suite.encrypt(bytes(new_gender, encoding = 'utf-8'))

        conn = pymysql.connect(host="localhost", user="root", password="password")
        cursor = conn.cursor()
        cursor.execute("use MODULE3")
        query = "select NAME from DATA where PHONE = %s"
        values = (phone)

        cursor.execute(query, values)

        response = cursor.fetchall()
        response = [x[0] for x in response]

        record_updated = False
        for name in response:
            try:
                decoded_name = cipher_suite.decrypt(name)
                query = "update DATA set PHONE = %s, NAME = %s, AGE = %s, GENDER = %s where NAME = %s"
                values = (new_phone, encrypted_name, encrypted_age, encrypted_gender, name)
                cursor.execute(query, values)
                conn.commit()
                record_updated = True
                break
            except Exception as e:
                # print(e)
                continue
        if record_updated:
            print("Record Updated")
            return True
        else:
            print("Record Could not be updated")
            return False

    except:
        print("Record could not be updated")
        return None

createTable()
conn.close()

if __name__ == '__main__':
    data = encrypt_data()
    store_data(data)

    fetch_data()