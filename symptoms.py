"""
Project By:
2024176 - Darshan Bothra
2024369 - Namish Batra
2024203 - Divyansh Singhwal
2024521 - Shashank Kumar
2024161 - Chinmay Chaudhari
2024170 - Daksh Singh
"""

import re
from datetime import datetime
import json
import requests

global questions
questions = [
    "Please describe your symptoms. (mandatory)",
    "How frequent are these diseases (eg. occasionally, quiet frequently, all the time)? (mandatory)",
    "When did you start noticing these symptoms?\nPlease write an overall start time since you started noticing these symptoms (mandatory)",
    "How severe are these symptoms on the scale of 1 (mild) to 10 (extremely severe)?\nPlease enter an overall severity of the symptoms you are having, rate according to the degree of uneasiness or pain that you are having (mandatory)"
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

    i = 0
    for symptom in data:
        if symptom in symptom_input_string:
            if symptom not in symptoms_detected:
                symptoms_detected.append(symptom)
    while i< len(tokens):
        token = tokens[i]
        if token in data:
            if token not in symptoms_detected:
                symptoms_detected.append(token)
                continue
        else:
            for symptom in data:
                if token in data[symptom]:
                    if symptom not in symptoms_detected:
                        symptoms_detected.append(symptom)
                        break
                else:
                    for element in data[symptom]:
                        if token in element:
                            if element in symptom_input_string.lower():
                                if symptom not in symptoms_detected:
                                    symptoms_detected.append(symptom)
                                    break
            else:
                if token == "pain" and tokens[i+1] == "in":
                    after_and = ""
                    all_pain = []
                    if tokens[i+2] == "my":
                        symptom = f"pain in {tokens[i+3]}"
                        all_pain.append(symptom)
                        if tokens[i+4] == "and":
                            after_and = tokens[i+5]
                    else:
                        symptom  = f"pain in {tokens[i + 2]}"
                        all_pain.append(symptom)
                        if tokens[i+3] == "and":
                            after_and = tokens[i+4]
                    if after_and:
                        all_pain.append(f"pain in {after_and}")
                    for symptom in all_pain:
                        if symptom not in symptoms_detected:
                            symptoms_detected.append(symptom)

        i+=1

    return symptoms_detected
def getFrequency(response_tokens: list[str])->str:
    freq = ["occasionally", "frequent", "rarely", "moderately", "frequently", "rare", "intermittently", "mild", "all the time"]
    adject = ["very", "quite", "quiet"]
    special = ["pain", "hurt"]
    result = []
    i = 0
    while (i < len(response_tokens)):
        if response_tokens[i] in adject:
            if response_tokens[i + 1] in freq:
                result = " ".join([response_tokens[i], response_tokens[i + 1]])
                break
        elif response_tokens[i] in freq:
            result = response_tokens[i]
            break
        if response_tokens[i] in special:
            result = " ".join(response_tokens[i:])
            break
        for fre in freq:
            if fre in " ".join(response_tokens):
                result = freq
                break
        i += 1
    return result
def getStart(response_tokens: list[str])->str:
    start: str = ""
    time_periods = ["decades", "years", "months", "weeks", "days", "hours", "minutes", "seconds"]
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

    for t in time_periods:
        if t in response_tokens:
            for token in response_tokens:
                if token.isnumeric():
                    start = f"{token} {response_tokens[response_tokens.index(token)+1]}"
                    break
    else:
        for token in  response_tokens:
            if token.isnumeric():
                if int(token) >= 1 and int(token) <= 31:
                    date = token
                else:
                    date =""
                for m in months:
                    if m in response_tokens:
                        month = m
                        break
                else:
                    month = ""
                for token in response_tokens:
                    if token.isnumeric() and int(token) >1900:
                        year = token
                    else:
                        year = ""

                if date and month:
                    start = f"{date} {months} {year}"

    return start
def getScale(response_tokens: list[str])->float:
    numeric_data: list[int] = [];
    for token in response_tokens:
        if token.isnumeric():
            if int(token) >=1 and int(token) <= 10:
                numeric_data.append(int(token))
    return sum(numeric_data)/len(numeric_data)
def followUpQuestions(symptoms_identified: list[str]):
    data = [", ".join(symptoms_identified)]
    for question in questions[1:]:
        print(f"Assistant: {question}")
        response: str = input("You: ")
        response_token = tokenize(response)
        if "frequent" in question:
            frequency = getFrequency(response_token)
            if frequency:
                print(f"Assistant: {frequency} it is. Very sorry to hear that")
                data.append(frequency)
            else:
                print("Assistant: Sorry I couldn't get that. Please try stating it in a different way.")
                second_inp: str = input("You: ")
                second_frq = getFrequency(tokenize(second_inp))
                if second_frq:
                    print(f"Assistant: {second_frq} it is. Very sorry to hear that")
                    data.append(second_frq)
                else:
                    print("Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")
        elif "noticing" in question:
            start = getStart(response_token)
            if start:
                print("Okay, noted!")
                data.append(start)
            else:
                print("Assistant: Sorry I couldn't get that. Please try stating it in a different way.")
                second_inp: str = input("You: ")
                second_start = getStart(tokenize(second_inp))
                if second_start:
                    print("Okay, noted!")
                    data.append(second_start)
                else:
                    print(
                        "Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")
        elif "scale" in question:
            scale = getScale(response_token)
            if scale:
                if int(scale) >= 6:
                    print(f"Its a {scale}! it is great that you are here, we can get you diagnosed properly now!")
                else:
                    print(f"Recorded {scale}, they seem mild, but its great that you're cautious")
                data.append(scale)
            else:
                print("Assistant: Sorry I couldn't get that. Please try stating it in a different way.")
                second_inp: str = input("You: ")
                second_scale = getScale(tokenize(second_inp))
                if second_scale:
                    if int(scale) >= 6:
                        print(f"Its a {second_scale}! it is great that you are here, we can get you diagnosed properly now!")
                    else:
                        print(f"Recorded {second_scale}, they seem mild, but its great that you're cautious")
                    data.append(second_scale)
                else:
                    print(
                        "Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")


    isOrtho: bool = checkOrthoSymptoms(symptoms_identified)
    data.append(isOrtho)
    if isOrtho:
        print("Assistant: You are required to see an orthopedic doctor")
    else:
        print("You are not required to see an orthopedic doctor")
def checkOrthoSymptoms(symptom_list: list[str])->bool:
    with open("ortho-symptoms.json", "r") as f:
        symptom_data = json.load(f)

    symptoms_list = []
    for data in symptom_data["Symptoms_orthopedic"]:
        symptoms_list.append(data["Symptom"].lower())
    matched: list[str] = []
    for symptom in symptom_list:
        if symptom.lower() in symptoms_list or "pain in" in symptom:
            matched.append(symptom)

    if len(matched) >= 3:
        return True
    elif len(matched)/len(symptom_list) >= 0.6:
        return True
    return False


import re
import json


def extract_full_name(user_input):
    phrases = ["my name is", "call me", "it's", "it is", "i am", "i'm", "name’s", "they call me", "i’m"]
    user_input = user_input.strip().lower()
    for phrase in phrases:
        if phrase in user_input:
            name_part = user_input.split(phrase, 1)[1].strip()
            full_name = re.sub(r'[^\w\s]', '', name_part)
            return full_name.title()
    if re.match(r'^[a-zA-Z\s]+$', user_input):
        return user_input.title()
    return "Could not extract a proper name."


def load_age_mapping():
    try:
        with open('a2.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: age_mapping.json file not found!")
        return None


def extract_age(text, age_data):
    ages = []
    numeric_pattern = r'\b([1-9]|[1-9][0-9]|1[0-4][0-9]|150)\b'
    numeric_matches = re.finditer(numeric_pattern, text)
    for match in numeric_matches:
        age = int(match.group(1))
        if str(age) in age_data["age"]:
            ages.append(age)
    text_lower = text.lower()
    for num_str, words in age_data["age"].items():
        if any(word in text_lower for word in words):
            ages.append(int(num_str))
    return max(ages) if ages else None


def extract_gender(user_input):
    male_keywords = ["male", "man", "boy", "guy"]
    female_keywords = ["female", "woman", "girl", "lady"]
    nonbinary_keywords = ["non binary", "nonbinary", "non-binary", "nb", "gender-neutral"]
    prefer_not_keywords = ["prefer not to say", "no comment", "rather not say", "prefer not to disclose"]

    user_input = user_input.strip().lower()
    words = user_input.split()

    if any(word in words for word in male_keywords):
        return "Male"
    elif any(word in words for word in female_keywords):
        return "Female"
    elif any(word in words for word in nonbinary_keywords):
        return "Non-Binary"
    elif any(word in words for word in prefer_not_keywords):
        return "Prefer Not to Say"
    return "Prefer Not to Say."


def find_disease_match(user_input, disease_file):
    try:
        with open(disease_file, 'r') as file:
            disease_data = json.load(file)
    except FileNotFoundError:
        return "Disease file not found."
    except json.JSONDecodeError:
        return "Error decoding the JSON file."

    user_input = user_input.lower().strip()

    if "diabetes" in user_input or "sugar" in user_input or "sugar diabetes" in user_input or "diabetic" in user_input:
        return ["Diabetes"]

    matches = []
    if "cancer" in user_input:
        cancer_types = [
            "Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Prostate Cancer",
            "Pancreatic Cancer", "Skin Cancer", "Leukemia", "Lymphoma", "Ovarian Cancer"
        ]
        return cancer_types

    for disease, synonyms in disease_data.items():
        if disease.lower() in user_input:
            matches.append(disease)
            continue
        for synonym in synonyms:
            if synonym.lower() in user_input:
                matches.append(disease)
                break

    return matches


def handle_medical_conditions(user_input, disease_file):
    stored_conditions = []

    if "diabetic" in user_input or "diabetes" in user_input or "sugar" in user_input or "sugar diabetes" in user_input:
        stored_conditions.append("Diabetes")
        if "type 1" in user_input:
            stored_conditions.append("Type 1 Diabetes")
        elif "type 2" in user_input:
            stored_conditions.append("Type 2 Diabetes")

    matches = find_disease_match(user_input, disease_file)
    if matches:
        if len(matches) > 1:
            print("Chatbot: Multiple diseases found. Please choose which one best describes your condition:")
            for idx, condition in enumerate(matches):
                print(f"{idx + 1}. {condition}")
            choice = int(input("Chatbot: Please enter the number corresponding to your condition.\nUser input: "))
            return [matches[choice - 1]]
        else:
            stored_conditions.append(matches[0])

    if not stored_conditions:
        print("Chatbot: Could not find any matches in the database.")
        user_input = input(
            "Chatbot: Is there another, more scientific name for your disease?\nUser input: ").strip().lower()
        matches = find_disease_match(user_input, disease_file)
        if matches:
            stored_conditions.extend(matches)
        else:
            print("Chatbot: Sorry, I couldn’t find anything in the database. Could you try again?")

    return stored_conditions


def getDemographics():
    name_input = input("Chatbot: Hello, what is your name?\nUser input: ")
    full_name = extract_full_name(name_input)
    print(f"Chatbot: Nice to meet you, {full_name}!")

    age_input = input("Chatbot: How old are you?\nUser input: ")
    age_data = load_age_mapping()
    age = extract_age(age_input, age_data)
    if age:
        print(f"Chatbot: You are {age} years old.")
    else:
        print("Chatbot: I couldn't extract your age, but that's okay.")

    gender_input = input("Chatbot: What is your gender?\nUser input: ")
    gender = extract_gender(gender_input)
    print(f"Chatbot: You identified as {gender}.")

    user_input = input("Chatbot: Do you have a medical condition or disease? (yes/no)\nUser input: ").strip().lower()

    while user_input not in ["yes", "no"]:
        print("Chatbot: Please enter a valid response.")
        user_input = input(
            "Chatbot: Do you have a medical condition or disease? (yes/no)\nUser input: ").strip().lower()

    if user_input == "yes":
        user_input = input(
            "Chatbot: Could you please tell me about any previous medical conditions or diseases?\nUser input: ")
        disease_file = "disease2.json"
        medical_conditions = handle_medical_conditions(user_input, disease_file)

        if medical_conditions:
            print(f"\nChatbot: {', '.join(medical_conditions)}")
        else:
            print("\nChatbot: No specific medical conditions noted.")

    elif user_input == "no":
        print("\nChatbot: No medical condition noted.")



def main()->None:
    """
    main call stack of the program. Initializes and runs the chat algorithms
    :return: None
    """

    # Greet User
    greet()

    #Get user Demographics
    getDemographics()

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
        print(f"Assistant: Your response has been duly noted. A report will be generated shortly, please be ready with your documents and test results if any.\nThankyou Very much for your patience :)")
    else:
        print("Assistant: I was not able to identify any symptoms")

if __name__ == '__main__':
    main()
