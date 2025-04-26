import google.generativeai as genai
from datetime import datetime
import json
import re
import speech_recognition as sr


def audioo():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening your command........")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print('analyzing your command........')
        text = r.recognize_google(audio, language='en-in')
        print(f'you said:{text}')
    except Exception as e:
        print('say that again please........')
        return 'None'
    return text


questions = [
    "Please describe your symptoms. (mandatory)",
    "How frequent are these diseases (eg. occasionally, quiet frequently, all the time)? (mandatory)",
    "When did you start noticing these symptoms?\nPlease write an overall start time since you started noticing these symptoms (mandatory)",
    "How severe are these symptoms on the scale of 1 (mild) to 10 (extremely severe)?\nPlease enter an overall severity of the symptoms you are having, rate according to the degree of uneasiness or pain that you are having (mandatory)"
]


def cont():
    print("Assistant: Do you wish to run the program again?(y/n)")
    command = input("Waiting for your response: ")
    if command.lower() == "y":
        main()
    elif command.lower() == "n":
        print("Quitting...")
        return
    else:
        cont()


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
    return None


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
    return "Unrecognized, Kindly type your gender"


def check_medical_history(user_input, yn) -> list[str]:
    def find_disease_match(user_input):
        diseases: list[str] = []
        user_input = user_input.lower().strip()
        prompt = f"what are all the diseases from the following prompt (just the words) else return None:{user_input}"
        try:
            response = model.generate_content(prompt)
            l = response.text.split(",")
            for disease in l:
                diseases.append(disease.lower().strip())
            return diseases
        except:
            return []

    while yn not in ["yes", "no"]:
        print("Assistant: Please enter a valid response.")
        yn = input(
            "Assistant: Do you have a medical condition or disease? (yes/no)\nUser input: ").strip().lower()
        if yn in ("yes", "no"):
            break

    if yn == "yes":

        matches = find_disease_match(user_input)

        if matches:
            print(f"\nAssistant: Medical conditions noted {', '.join(matches)}")
            return matches
        else:
            print("Assistant: Could not find any matches in the database.")
            user_input = input(
                "Assistant: Could you provide a more specific name for your disease?\nUser input: ").strip().lower()
            matches = find_disease_match(user_input)

            if matches:
                print(f"\nAssistant: Medical conditions noted {', '.join(matches)}")
                return matches
            else:

                return []

    elif yn == "no":
        print("\nAssistant: No medical condition noted.")
        return []


def configureLLM() -> None:
    with open("apikey.txt", "r") as f:
        API_KEY = f.read()

    genai.configure(api_key=API_KEY, transport="rest")
    global model
    model = genai.GenerativeModel("gemini-1.5-flash")


def greet() -> None:
    hour: int = int(str(datetime.now())[11:13])

    if hour >= 17:
        print("Assistant: Good Evening. I am your chat assistant, I will ask you some screening questions.")
    if hour >= 12:
        print("Assistant: Good Afternoon. I am your chat assistant, I will ask you some screening questions.")
    elif hour >= 3:
        print("Assistant: Good Morning. I am your chat assistant, I will ask you some screening questions.")
    else:
        print("Assistant: Hello! I am your chat assistant, I will ask you some screening questions.")


def getDemographics() -> list:
    global medical_conditions
    demographics_list: list = []
    full_name, age, gender, medical_conditions = None, None, None, None
    # name_input = input("Assistant: Hello, what is your name?\nUser input: ")
    print("Assistant: Hello, what is your name?")
    name_input = audioo()
    full_name = extract_full_name(name_input)
    if full_name == None:
        full_name = input("I couldn't get that, Please type your name: ")
    print(f"Assistant: Nice to meet you, {full_name}!")
    demographics_list.append(full_name)

    # age_input = input("Assistant: How old are you?\nUser input: ")
    print("Assistant: How old are you?")
    age_input = audioo()
    age_data = load_age_mapping()
    age = extract_age(age_input, age_data)
    if age == None:
        age = input("I couldn't get that, Please type your age: ")
    print(f"Assistant: You are {age} years old.")
    demographics_list.append(age)

    # gender_input = input("Assistant: What is your gender?\nUser input: ")
    print("Assistant: What is your gender?")
    gender_input = audioo()
    gender = extract_gender(gender_input)
    if gender == "Unrecognized, Kindly type your gender":
        gender = input("I couldn't recognize your gender, Kindly type it: ")
        print(f"Assistant: You identified as {gender}.")
        demographics_list.append(gender)
    else:
        print(f"Assistant: You identified as {gender}.")
        demographics_list.append(gender)

    yn = input("Assistant: Do you have a medical condition or disease? (yes/no)\nUser input: ").strip().lower()

    while yn not in ["yes", "no"]:
        print("Assistant: Please enter a valid response.")
        yn = input(
            "Assistant: Do you have a medical condition or disease? (yes/no)\nUser input: ").strip().lower()

    if yn == "yes":
        print(
            "Assistant: Could you please tell me about any previous medical conditions or diseases?\nUser input: ")
        user_input = audioo()
        medical_conditions = check_medical_history(user_input, yn)
        if medical_conditions:
            demographics_list.append(", ".join(medical_conditions))

        if not medical_conditions:
            print("\nAssistant: No specific medical conditions noted.")
            demographics_list.append(None)
    elif yn == "no":
        print("\nAssistant: No medical condition noted.")
        demographics_list.append(None)
    return demographics_list


def tokenize(input_string: str) -> list[str]:
    tokens: list[str] = []
    temp: list[str] = [x for x in input_string.split()]
    for i in range(len(temp)):
        word: str = temp[i]
        temp_word: str = ""
        for j in range(len(word)):
            if word[j].isalnum():
                temp_word += word[j].lower()
        tokens.append(temp_word)
    return tokens


def fetchSymptoms(prompt: str) -> list[str]:
    try:
        response = model.generate_content(
            f"what are all the symptoms from the following prompt, if the prompt mentions pain, include the areas of pain in the response as 'pain in and body part name' (just the words) else return None:{prompt}")
        symptoms = [x.strip() for x in response.text.split(",")]
        if symptoms[0] == None:
            return []
        return symptoms
    except Exception:
        pass


def getFrequency(response_tokens: list[str]) -> str:
    result = None

    user_string = " ".join(response_tokens)
    prompt: str = f"return just the word which symbolize frequency from the string without any line break (return the word only not a string or any sort of explanation, if there is no word which symbolizes frequency then donot return 'NONE'): {user_string}"
    response = model.generate_content(prompt)

    result = response.text.strip()
    if result == 'NONE':
        return None
    return result


def getStart(response_tokens: list[str]) -> str:
    start: str = ""
    user_inp = ", ".join(response_tokens)
    prompt = f"get the date (if there) or time ago(if there) from the given string (return just the start time ago/ date only do not change any decimal values if there): {user_inp}"
    try:
        response = model.generate_content(prompt)
        start = response.text.strip()
    except:
        pass

    return start


def getScale(response_tokens: list[str]) -> float:
    numeric_data: list[int] = []
    for token in response_tokens:
        if token.isnumeric():
            if int(token) >= 1 and int(token) <= 10:
                numeric_data.append(int(token))
    if len(numeric_data) == 0:
        return False
    return sum(numeric_data) / len(numeric_data)


def checkOrthoSymptoms(symptoms_identified: list[str], disease_list: list[str]) -> bool:
    symptom_str = ", ".join(symptoms_identified)
    disease_str = ""

    if disease_list:
        disease_str = "diseases are: "
        disease_str += ", ".join(disease_list)

    prompt = f"given the symptoms and suffering diseases of the patient, identify they should see the orthopedist just return true or false: symptoms are: {symptom_str} {disease_str}"
    response = model.generate_content(prompt)
    if response.text.strip() == "True":
        return True
    else:
        return False


def followUpQuestions(symptoms_identified: list[str]) -> list:
    data = [symptoms_identified]  # [symptoms, frequency, start, scale, isOrtho]
    for question in questions[1:]:
        print(f"Assistant: {question}")
        response: str = audioo()
        response_token = tokenize(response)
        if "frequent" in question:
            frequency = getFrequency(response_token)
            if frequency:
                print(f"Assistant: {frequency} it is. Very sorry to hear that")
                data.append(frequency)
            else:
                print("Assistant: Sorry I couldn't get that. Please type it in: ", end = "")
                second_inp: str = input()
                second_frq = getFrequency(tokenize(second_inp))
                if second_frq:
                    print(f"Assistant: {second_frq} it is. Very sorry to hear that")
                    data.append(second_frq)
                else:
                    print(
                        "Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")
                    data.append(None)
        elif "noticing" in question:
            start = getStart(response_token)
            if start:
                print("Okay, noted!")
                data.append(start)
            else:
                print("Assistant: Sorry I couldn't get that. Please type it in: ", end = "")
                second_inp: str = input()
                second_start = getStart(tokenize(second_inp))
                if second_start:
                    print("Okay, noted!")
                    data.append(second_start)
                else:
                    print(
                        "Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")
                    data.append(None)
        elif "scale" in question:
            scale = getScale(response_token)
            if scale:
                if int(scale) >= 6:
                    print(f"Its a {scale}! it is great that you are here, we can get you diagnosed properly now!")
                else:
                    print(f"Recorded {scale}, they seem mild, but its great that you're cautious")
                data.append(scale)


            else:
                print("Assistant: Sorry I couldn't get that. type it in: ", end = "")
                second_inp: str = input()
                second_scale = getScale(tokenize(second_inp))
                if second_scale:
                    if int(scale) >= 6:
                        print(
                            f"Its a {second_scale}! it is great that you are here, we can get you diagnosed properly now!")
                    else:
                        print(f"Recorded {second_scale}, they seem mild, but its great that you're cautious")
                    data.append(second_scale)
                else:
                    print(
                        "Assistant: Sorry I count' get that again. I will leave this for now, lets move on to the next question")
                    data.append(None)
    isOrtho: bool = checkOrthoSymptoms(symptoms_identified, medical_conditions)
    data.append(isOrtho)
    if isOrtho:
        print("Assistant: You are required to see an orthopedic doctor")
    else:
        print("You are not required to see an orthopedic doctor")
    return data


def main() -> list[str]:
    print("Assistant: Please describe your symptoms. (mandatory)")
    user_inp = audioo()
    symptoms_identified = fetchSymptoms(user_inp)

    if (symptoms_identified[0] == 'None'):
        print("Assistant: I was unable to recognize the symptoms")
        cont()
    else:
        print(f"Assistant: I have recognized {len(symptoms_identified)} symptoms\n {', '.join(symptoms_identified)}")
        patient_data = followUpQuestions(symptoms_identified)
        print(
            f"Assistant: Your response has been duly noted. A report will be generated shortly, please be ready with your documents and test results if any.\nThankyou Very much for your patience :)")
        return patient_data


def getPatientData(phone) -> dict:

    usr_tup = getDemographics()
    data = main()
    print(usr_tup, data)
    usr_tup.extend(data)
    patient_data = {
        "phone": phone,
        "name": usr_tup[0],
        "age": usr_tup[1],
        "gender": usr_tup[2],
        "diseases": usr_tup[3],
        "symptoms": ", ".join(usr_tup[4]),
        "frequency": usr_tup[5],
        "start-time": usr_tup[6],
        "severity": usr_tup[7],
        "orthoCheck": usr_tup[8],

    }
    return patient_data


if __name__ == '__main__':
    configureLLM()
    greet()
    getPatientData()
