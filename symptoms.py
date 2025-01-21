# Questions
'''
Symptoms.
Frequency.
Severity.
Any diseases you are already suffering from
'''

from datetime import datetime
import json

global questions
questions = [
    "Please describe your symptoms.",
    "How frequent are these diseases (eg. occasionally, quiet frequently, all the time)?",
    "When did you start noticing these symptoms?",
    "How severe are these diseases on the scale of 1 to 5?",
    "Any diseases you are currently suffering from?"
]


def greet()->None:
    greeting:str = ""
    hour_of_day = int(str(datetime.now())[11:13]) # get the hour of day to set the appropriate greeting
    if hour_of_day >= 12:
        greeting = "Good Afternoon"
    elif hour_of_day >= 17:
        greeting = "Good Evening"
    elif hour_of_day >=0:
        greeting = "Good Morning"

    print(f"{greeting} I'm your Chat Assistant")
    return None
def tokenize(input_string: str)->list[str]:
    tokens: list[str] = []
    temp: list[str] = [x for x in input_string.split()]
    for i in range(len(temp)):
        word: str= temp[i]
        temp_word: str = ""
        for j in range(len(word)):
            if word[j].isalnum():
                temp_word += word[j].lower()
        tokens.append(temp_word)

    return tokens
def identifySymptoms(symptom_input_string: str)->list[str]:
    tokens = tokenize(symptom_input_string)
    symptoms_detected: list[str] = []
    with open("symptoms.json", "r") as f:
        data = json.load(f)

    for token in tokens:
        if token in data:
            if token not in symptoms_detected:
                symptoms_detected.append(token)
        else:
            for symptom in data:
                if token in data[symptom]:
                    if symptom not in symptoms_detected:
                        symptoms_detected.append(symptom)
                else:
                    for element in data[symptom]:
                        if token in element:
                            if element in symptom_input_string.lower():
                                if symptom not in symptoms_detected:
                                    symptoms_detected.append(symptom)


    return symptoms_detected
    pass
    # open symptoms
def getFrequency(response_tokens: list[str]):
    pass

def getStart(response_tokens: list[str])->str:
    start: str = ""
    time_periods = ["decades", "years", "months", "weeks", "days", "hours", "minutes", "seconds"]
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

    pass

    return start
def getScale(response_tokens: list[str])->float:
    numeric_data: list[int] = [];
    for token in response_tokens:
        if token.isnumeric():
            if int(token) >=1 and int(token) <= 5:
                numeric_data.append(int(token))
    return sum(numeric_data)/len(numeric_data)
def getCurrentDiseases(response_tokens: list[str])->list[str]:
    diseases = []

    with open("diseases.json", "r") as f:
        data = json.load(f)

    for token in response_tokens:
        if response_tokens in data["diseases"]:
            diseases.append(token)

    return diseases



def followUpQuestions(symptoms_identified: list[str]):
    data = [", ".join(symptoms_identified)]
    for question in questions[1:]:
        print(f"Assistant: {question}")
        response: str = input("You: ")
        response_token = tokenize(response)
        if "frequent" in question:
            getFrequency(response_token)
        elif "noticing" in question:
            start = getStart(response_token)
        elif "scale" in question:
            scale = getScale(response_token)
            data.append(scale)
        elif "currently suffering" in question:
            current_diseases = getCurrentDiseases(response_token)
            if current_diseases != []:
                if (len(current_diseases) == 1):
                    data.append(current_diseases[0])
                else:
                    data.append(", ".join(current_diseases))


def main()->None:
    """
    main call stack of the program. Initializes and runs the chat algorithms
    :return: None
    """

    # Greet User
    greet()

    # Ask some demographics questions and store them in a database. (Divyansh Singhwal)
    """
    name, patient id, record number
    """
    # Ask symptoms and related questions

    # Question 1
    print(f"Assistant: {questions[0]}") # "Please describe your symptoms"
    symptom_user_input: str = input("You: ")
    symptoms_identified: list[str] = identifySymptoms(symptom_user_input)

    if symptoms_identified:
        # Give response to user
        symptom_count = len(symptoms_identified)
        print(f"Assistant: I was able to recognize {symptom_count} symptom(s)\n{', '.join(symptoms_identified)}")
        # store data in a database
        followUpQuestions(symptoms_identified)
    else:
        print("Assistant: I was not able to identify any symptoms")


if __name__ == '__main__':
    main()
