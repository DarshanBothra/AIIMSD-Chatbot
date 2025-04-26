import pymysql

conn= pymysql.connect(host="localhost",user="root",password="password")
cursor=conn.cursor()

def createTable():
    cursor.execute("show database")
    db = cursor.fetchall()
    if (("MODULE2", )) not in db:
        cursor.execute("create database MODULE2")
    cursor.execute("use MODULE2")
    cursor.execute("show tables")

    tables = cursor.fetchall()
    if (("DATA",) not in tables):

        cursor.execute(
            """
            create table DATA (
            APPOINTMENTID INTEGER PRIMARY KEY
            NAME VARCHAR (255),
            AGE VARCHAR (255),
            GENDER VARCHAR (255),
            DISEASES VARCHAR (255),
            SYMPTOMS VARCHAR (255),
            FREQUENCY VARCHAR (255),
            DURATION VARCHAR (255),
            SEVERITY VARCHAR (255),
            ORTHOCHECK VARCHAR (255)
            )
            """
        )
    else:
        print("Table already exists")
def store_data(name, age, gender, diseases, symptoms, frequency, duration, severity, orthoCheck):
    createTable()
    qry = "INSERT into DATA values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = name, age, gender, diseases, symptoms, frequency, duration, severity, str(orthoCheck)
    cursor.execute(qry, val)
    conn.commit()

conn.close()