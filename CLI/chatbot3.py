import google.generativeai as genai
from datetime import datetime
import json
import re
import speech_recognition as sr
from deep_translator import GoogleTranslator as gt
import tts
import asyncio

import speech_recognition as sr
from langdetect import detect, LangDetectException

# Supported languages: English, Hindi, French, and German
LANGUAGE_CODE_MAP = {
    'en': 'en-US',
    'hi': 'hi-IN',
    'fr': 'fr-FR',
    'de': 'de-DE'
}


def speech_to_text_multilingual():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening (This model supports English, Hindi, French, and German)...")
        recognizer.pause_threshold = 1.2
        try:
            audio = recognizer.listen(source, timeout=10)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            return None

    # Try transcription in each language and validate with langdetect
    for lang_code, google_lang in LANGUAGE_CODE_MAP.items():
        try:
            text = recognizer.recognize_google(audio, language=google_lang)
            detected = detect(text)

            if detected == lang_code:
                return text
        except sr.UnknownValueError:
            continue  # Try next language
        except sr.RequestError as e:
            print(f"Google API error for {lang_code}: {e}")
            continue
        except LangDetectException:
            continue

    print("❌ Could not detect or transcribe the speech in supported languages.")
    return None


def getInteractionType():
    print("Please choose interaction type.\n1 - for text-based\n2 - for voice-based")
    int_type = None

    while (int_type == None):
        int_type = input("Waiting for your command: ")
        if (int_type == '1'):
            print("You have chosen text-based interaction")
            break
        elif (int_type == '2'):
            print("You have chosen voice-based interaction")
            break
        else:
            print("Invalid Command!\n1 - for text-based\n2 - for voice-based")
            int_type = None

    return int_type

interaction_type = getInteractionType()
def translate(text: str, var: str) -> str:
    t_text = (gt(source='auto', target=var).translate(text))
    return t_text


def audioo():
    result = speech_to_text_multilingual()
    text = translate(result, 'en')
    return text


# def audioo():
#     r = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("listening your command........")
#         r.pause_threshold = 1
#         audio = r.listen(source)
#     try:
#         print('analyzing your command........')
#         text = r.recognize_google(audio, language='en-in')
#         print(f'you said:{text}')
#     except Exception as e:
#         print('say that again please........')
#         return 'None'
#     return text

def translate(text: str, var: str) -> str:
    t_text = (gt(source='auto', target=var).translate(text))
    return t_text


questions = [
    "Please describe your symptoms. (mandatory)",
    "How frequent are these diseases (eg. occasionally, quiet frequently, all the time)? (mandatory)",
    "When did you start noticing these symptoms?\nPlease write an overall start time since you started noticing these symptoms (mandatory)",
    "How severe are these symptoms on the scale of 1 (mild) to 10 (extremely severe)?\nPlease enter an overall severity of the symptoms you are having, rate according to the degree of uneasiness or pain that you are having (mandatory)"
]


def cont(var):
    print("Assistant: Do you wish to run the program again?(y/n)")
    command = input("Waiting for your response: ")
    if command.lower() == "y":
        main(var)
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


def greet(var) -> None:
    hour: int = int(str(datetime.now())[11:13])

    if hour >= 17:
        t_text = translate("Good Evening. I am your chat assistant, I will ask you some screening questions.", var)
        print("Assistant:", t_text)
        # print(gt(source='auto',target=var).translate("Assistant: Good Evening. I am your chat assistant, I will ask you some screening questions."))
    if hour >= 12:
        t_text = translate("Good Afternoon. I am your chat assistant, I will ask you some screening questions.", var)
        print("Assistant:", t_text)
        # print(gt(source='auto',target=var).translate("Assistant: Good Afternoon. I am your chat assistant, I will ask you some screening questions."))
    elif hour >= 3:
        t_text = translate("Good Morning. I am your chat assistant, I will ask you some screening questions.", var)
        print("Assistant:", t_text)
        # print(gt(source='auto',target=var).translate("Assistant: Good Morning. I am your chat assistant, I will ask you some screening questions."))
    else:
        print(gt(source='auto', target=var).translate(
            "Assistant: Hello! I am your chat assistant, I will ask you some screening questions."))


def language_prefer() -> str:
    inp = input("Enter 1-for englsh , 2.-HIndi, 3.-french, 4.-german")
    var = ""
    if inp == '1':
        var = "en"
    elif inp == '2':
        var = "hindi"
    elif inp == '3':
        var = "fr"
    elif inp == '4':
        var = 'german'
    else:
        print("Enter valid choice:")
        language_prefer()
    return var


def getDemographics(var: str) -> list:
    global medical_conditions
    demographics_list: list = []
    full_name, age, gender, medical_conditions = None, None, None, None
    # name_input = input("Assistant: Hello, what is your name?\nUser input: ")
    t_text1 = translate("what is your name", var)
    print(t_text1)
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(tts.text_to_speech(t_text1, var))
    try:
        name_input = audioo() if interaction_type == '2' else input("Enter input: ")
    except Exception as e:
        name_input = input("Couldn't fetch name.Kindly type it: ")

    full_name = extract_full_name(name_input)

    t_text2 = translate("Nice to meet you", var)
    print("Assistant:", t_text2)
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(tts.text_to_speech(t_text2, var))
    demographics_list.append(full_name)

    # age_input = input("Assistant: How old are you?\nUser input: ")
    t_text3 = translate("what is your age", var)
    print("Assistant:", t_text3)
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(tts.text_to_speech(t_text3, var))
    try:
        age_input = audioo() if interaction_type == '2' else input("Enter input: ")
    except Exception as e:
        age_input = input("Could not fetch age. Kindly Enter it: ")
    age_data = load_age_mapping()
    age = extract_age(age_input, age_data)
    if age:
        o = f"Assistant: You are {age} years old."
        t_text4 = translate(o, var)
        print(t_text4)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(t_text4, var))
        demographics_list.append(age)
    else:
        t_text4 = translate("I couldn't extract your age, but that's okay.", var)
        print("Assistant:", t_text4)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(t_text4, var))

    # gender_input = input("Assistant: What is your gender?\nUser input: ")
    t_text5 = translate("what is your gender.....", var)
    print("Assistant:", t_text5)
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(tts.text_to_speech(t_text5, var))
    try:
        gender_input = audioo() if interaction_type == '2' else input("Enter input: ")

    except Exception as e:
        gender_input = input("Gender could not be fetched. Kindly type it: ")

    gender = extract_gender(gender_input)
    if gender == "Unrecognized, Kindly type your gender":
        t_text6 = translate("I couldn't recognize your gender, Kindly type it: ", var)
        print("Assistant:", t_text6)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(t_text6, var))
        gender = input(
            gt(source='auto', target=var).translate("Enter Your Gender: "))  # needs to be converted to english
        oo = f"You identified as {gender}."
        print("Assistant:", translate(oo, var))
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(translate(oo, var), var))
        demographics_list.append(gender)
    else:
        oa = f"You identified as {gender}."
        print("Assistant:", translate(oa, var))
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(translate(oa, var), var))
        demographics_list.append(gender)

    print("Assistant:", translate("Assistant: Do you have a medical condition or disease? (yes/no)", var), "\n",
          "user input")
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(
            tts.text_to_speech(translate("Assistant: Do you have a medical condition or disease? (yes/no)", var), var))
    yn = input().strip().lower()
    yn = translate(yn, "en")

    while yn not in ['yes', 'no',translate(yn,var),translate(yn,var)]:
        print("Assistant:", translate(" Please enter a valid response.", var))
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(translate(" Please enter a valid response.", var), var))
        # print(gt(source='auto',target=var).translate("Assistant:))
        print("Assistant:", translate("Assistant: Do you have a medical condition or disease? (yes/no)", var), "\n",
              "user input")
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(
                tts.text_to_speech(translate("Assistant: Do you have a medical condition or disease? (yes/no)", var),
                                   var))
        yn = input().strip().lower()
        yn = translate(yn, "en")

    if yn == 'yes'or yn == translate(yn,var):
        t_text7 = translate(" Could you please tell me about any previous medical conditions or diseases?", var)
        print("Assistant:", t_text7, "\nUser input:")
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(t_text7, var))
        # print(gt(source='auto',target=var).translate(
        # "Assistant:\nUser input: "))
        try:
            user_input = audioo() if interaction_type == '2' else input("Enter input: ")
        except Exception as e:
            user_input = input("Could not fetch response. Kindly type it: ")
        medical_conditions = check_medical_history(user_input, yn)
        if medical_conditions:
            demographics_list.append(", ".join(medical_conditions))

        if not medical_conditions:
            t_text8 = translate("No specific medical conditions noted.", var)
            print("Assistant:", t_text8)
            if (interaction_type == '2'):  # If voice based interaction chosen
                asyncio.run(tts.text_to_speech(t_text8, var))
            demographics_list.append(None)

    elif yn == 'no' or yn == translate(yn,var):
        t_text7 = translate(" No medical condition noted.", var)
        print("\nAssistant:", t_text7)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(t_text7, var))
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
    prompt: str = f"return just the word which symbolize frequency from the string without any line break (return the word only along with the adjective if any, not a string or any sort of explanation): {user_string}"
    response = model.generate_content(prompt)
    result = response.text.strip()
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
    numeric_data: list[float] = [];
    for token in response_tokens:
        if token.isnumeric():
            if float(token) >= 1 and float(token) <= 10:
                numeric_data.append(float(token))
    if numeric_data:
        return sum(numeric_data) / len(numeric_data)
    else:
        return None


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


def followUpQuestions(symptoms_identified: list[str], var) -> list:
    data = [symptoms_identified]  # [symptoms, frequency, start, scale, isOrtho]
    fques = {}
    for i in questions[1:]:
        x = (translate(i, var))
        fques.update({i: x})
    # print(fques)
    for q, question in fques.items():
        print(f"Assistant: {question}")
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(question, var))
        try:
            response: str = audioo() if interaction_type == '2' else input("Enter input: ")
        except Exception as e:
            response = input("Could not fetch response. Kindly type it: ")
        response_token = tokenize(response)
        if "frequent" in q:
            frequency = getFrequency(response_token)
            if frequency:
                print(f"Assistant: {translate('it is. Very sorry to hear that', var)}")
                if (interaction_type == '2'):  # If voice based interaction chosen
                    asyncio.run(tts.text_to_speech(translate('it is. Very sorry to hear that', var), var))
                print(frequency)
                data.append(frequency)
            else:
                print(
                    f"Assistant: {translate('''Sorry I couldn't get that. Please try stating it in a different way''', var)}")
                if (interaction_type == '2'):  # If voice based interaction chosen
                    asyncio.run(tts.text_to_speech(
                        translate('''Sorry I couldn't get that. Please try stating it in a different way''', var), var))
                try:
                    second_inp: str = audioo() if interaction_type == '2' else input("Enter input: ")
                except Exception as e:
                    second_inp = input("Could not fetch the response. Kindly type it: ")
                second_frq = getFrequency(tokenize(second_inp))
                if second_frq:
                    print(f"Assistant: {second_frq} {translate('it is. Very sorry to hear that', var)}")
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(translate('it is. Very sorry to hear that', var), var))
                    data.append(second_frq)
                else:
                    print("Assistant:", translate(
                        "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                        var))
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(translate(
                            "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                            var), var))
                    data.append(None)
        elif "noticing" in q:
            start = getStart(response_token)
            if start:
                print(translate("Okay, noted!", var))
                if (interaction_type == '2'):  # If voice based interaction chosen
                    asyncio.run(tts.text_to_speech(translate("Okay, noted!", var), var))
                data.append(start)
            else:
                print("Assistant:",
                      translate("Sorry I couldn't get that. Please try stating it in a different way.", var))
                if (interaction_type == '2'):  # If voice based interaction chosen
                    asyncio.run(tts.text_to_speech(
                        translate("Sorry I couldn't get that. Please try stating it in a different way", var), var))
                try:
                    second_inp: str = audioo() if interaction_type == '2' else input("Enter input: ")
                except Exception as e:
                    second_inp = input("Could not fetch response. Kindly type it: ")
                second_start = getStart(tokenize(second_inp))
                if second_start:
                    print("Okay, noted!")
                    data.append(second_start)
                else:
                    print(
                        "Assistant:", translate(
                            "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                            var))
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(translate(
                            "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                            var), var))
                    data.append(None)

        elif "scale" in q:
            scale = getScale(response_token)
            if scale:
                if int(scale) >= 6:
                    print(translate(
                        f"Its a {scale}! it is great that you are here, we can get you diagnosed properly now!", var))
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(translate(
                            f"Its a {scale}! it is great that you are here, we can get you diagnosed properly now!",
                            var), var))
                else:
                    print(translate(f"Recorded {scale}, they seem mild, but its great that you're cautious", var))
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(
                            translate(f"Recorded {scale}, they seem mild, but its great that you're cautious", var),
                            var))
                data.append(scale)


            else:
                print("Assistant:",
                      translate("Sorry I couldn't get that. Please type stating it in a different way.", var))
                if (interaction_type == '2'):  # If voice based interaction chosen
                    asyncio.run(tts.text_to_speech(
                        translate("Sorry I couldn't get that. Please type stating it in a different way.", var), var))
                try:
                    second_inp: str = audioo() if interaction_type == '2' else input("Enter input: ")
                except Exception as e:
                    second_inp = input("Could not fetch response. Kindly type it: ")
                second_scale = getScale(tokenize(second_inp))
                if second_scale:
                    if int(scale) >= 6:
                        print(
                            translate(
                                f"Its a {second_scale}! it is great that you are here, we can get you diagnosed properly now!",
                                var))
                        if (interaction_type == '2'):  # If voice based interaction chosen
                            asyncio.run(tts.text_to_speech(
                                translate(
                                    f"Its a {second_scale}! it is great that you are here, we can get you diagnosed properly now!",
                                    var),
                                var))
                    else:
                        print(translate(f"Recorded {second_scale}, they seem mild, but its great that you're cautious",
                                        var))
                        if (interaction_type == '2'):  # If voice based interaction chosen
                            asyncio.run(tts.text_to_speech(translate(
                                f"Recorded {second_scale}, they seem mild, but its great that you're cautious", var),
                                                           var))
                    data.append(second_scale)
                else:
                    print(
                        "Assistant:", translate(
                            "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                            var))
                    if (interaction_type == '2'):  # If voice based interaction chosen
                        asyncio.run(tts.text_to_speech(
                            translate(
                                "Sorry I count' get that again. I will leave this for now, lets move on to the next question",
                                var), var))
                    data.append(None)
    isOrtho: bool = checkOrthoSymptoms(symptoms_identified, medical_conditions)
    data.append(isOrtho)
    if isOrtho:
        verdict = translate("You are required to see an orthopedic doctor", var)
        print("Assistant:", verdict)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(verdict, var))

    else:
        verdict = translate("You are not required to see an orthopedic doctor", var)
        print("Assistant: ", verdict)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(verdict, var))

    return data


def main(var) -> list[str]:
    print("Assistant:", translate("Please describe your symptoms. (mandatory)", var))
    if (interaction_type == '2'):  # If voice based interaction chosen
        asyncio.run(tts.text_to_speech(translate("Please describe your symptoms. (mandatory)", var), var))
    try:
        user_inp = audioo() if interaction_type == '2' else input("Enter input: ")
    except Exception as e:
        user_inp = input("Could not fetch response. Kindly type it: ")
    symptoms_identified = fetchSymptoms(user_inp)

    if (symptoms_identified[0] == 'None'):
        text = translate("I was unable to recognize the symptoms", var)
        print("Assistant:", text)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(text, var))

        cont(var)
    else:
        print(f"Assistant: I have recognized {len(symptoms_identified)} symptoms\n {', '.join(symptoms_identified)}")
        patient_data = followUpQuestions(symptoms_identified, var)
        text = translate(
            "Your response has been duly noted. A report will be generated shortly, please be ready with your documents and test results if any.\nThankyou Very much for your patience :)",
            var)
        print(
            f"Assistant:", text)
        if (interaction_type == '2'):  # If voice based interaction chosen
            asyncio.run(tts.text_to_speech(text, var))
        return patient_data


def getPatientData(var: str) -> dict:
    usr_tup = getDemographics(var)
    data = main(var)
    usr_tup.extend(data)
    patient_data = {
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
    var = language_prefer()
    greet(var)
    getPatientData(var)