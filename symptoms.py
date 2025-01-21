import re
from datetime import datetime
import json
import requests

global questions
questions = [
    "Please describe your symptoms.",
    "How frequent are these diseases (eg. occasionally, quiet frequently, all the time)?",
    "When did you start noticing these symptoms?",
    "How severe are these symptoms on the scale of 1 to 10?"
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
                    symptom  = f"pain in {tokens[i + 2]}"
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
    return False
def extract_full_name(user_input):
    """Extract the full name from You ."""
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
    """Extract age from You  using numeric and word-based matching."""
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
    """Extract gender from You ."""
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
def check_medical_history(user_input):
    """Check if the input contains any medical condition from the list."""
    try:
        with open('disease.json', 'r') as f:
            disease_data = json.load(f)
    except FileNotFoundError:
        print("Error: disease.json file not found!")
        return None

    medical_conditions = []
    user_input = user_input.lower()

    for disease in disease_data["diseases"]:
        if disease.lower() in user_input:
            medical_conditions.append(disease)

    return medical_conditions
def getDemographics():
    """Run the merged chatbot conversation."""

    user_input = input("Chatbot: Hello, what’s your name?\nYou : ")
    full_name = extract_full_name(user_input)
    print(f"\nChatbot: Hi, {full_name}, what’s your age?")

    age_data = load_age_mapping()
    if not age_data:
        return
    user_input = input("You : ")
    age = extract_age(user_input, age_data)
    age_response = f"{age}" if age is not None else "Could not determine age."
    print(
        f"\nChatbot: Your age is {age_response}. What’s your gender? (e.g., Male, Female, Non-binary, Prefer not to say)")

    user_input = input("You : ")
    gender = extract_gender(user_input)
    print(f"\nChatbot: You selected: {gender}.")

    user_input = input("\nChatbot: Could you please tell me about any previous medical conditions or diseases?\nYou : ")
    medical_conditions = check_medical_history(user_input)

    if medical_conditions:
        print("\nChatbot: Medical history has been noted.")
    else:
        print("\nChatbot: No specific medical conditions noted.")
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
