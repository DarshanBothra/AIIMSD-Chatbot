def readCredentials():
    with open("credentials/patients.txt", "r") as f:
        content = f.readlines()
    
    patients = dict([x.strip().split(",") for x in content])
    

    print(patients)


readCredentials()