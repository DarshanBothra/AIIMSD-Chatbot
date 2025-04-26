import streamlit as st
import edge_tts
import asyncio
import os
import time
import json
import pandas as pd
import re
from datetime import datetime
import pymysql
from cryptography.fernet import Fernet
from io import BytesIO
import base64
import google.generativeai as genai

# Initializing session states
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'̀
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'key' not in st.session_state:
    st.session_state.key = None

# Load language data
languages = {
    "en": {"code": "en", "name": "English", "voice": "en-US-JennyNeural"},
    "hindi": {"code": "hi", "name": "Hindi", "voice": "hi-IN-SwaraNeural"},
    "fr": {"code": "fr", "name": "French", "voice": "fr-FR-DeniseNeural"},
    "de": {"code": "de", "name": "German", "voice": "de-DE-Stefan-Male"}
}

# Create directories if they don't exist
os.makedirs('credentials', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Initialize credential files if they don't exist
if not os.path.exists('credentials/patients.txt'):
    with open('credentials/patients.txt', 'w') as f:
        pass
if not os.path.exists('credentials/admins.txt'):
    with open('credentials/admins.txt', 'w') as f:
        f.write("admin,admin123\n")
if not os.path.exists('keymap.txt'):
    with open('keymap.txt', 'w') as f:
        pass
if not os.path.exists('a2.json'):
    with open('a2.json', 'w') as f:
        age_data = {"age": {}}
        for i in range(1, 101):
            age_data["age"][str(i)] = [str(i), f"{i} years old", f"{i} years",
                                       f"{i} year old" if i == 1 else f"{i} years old"]
        json.dump(age_data, f)

def configureLLM() -> None:
    with open("apikey.txt", "r") as f:
        API_KEY = f.read()

    genai.configure(api_key=API_KEY, transport="rest")
    global model
    model = genai.GenerativeModel("gemini-1.5-flash")
# Database setup functions
def setup_database():
    try:
        conn = pymysql.connect(host="localhost", user="root", password="password")
        cursor = conn.cursor()

        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        if ('MODULE3',) not in databases:
            cursor.execute("CREATE DATABASE MODULE3")

        cursor.execute("USE MODULE3")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if ('DATA',) not in tables:
            cursor.execute("""
            CREATE TABLE DATA (
                PHONE VARCHAR(255), 
                NAME LONGBLOB,
                AGE LONGBLOB,
                GENDER LONGBLOB,
                DISEASES LONGBLOB,
                SYMPTOMS LONGBLOB,
                FREQUENCY LONGBLOB,
                DURATION LONGBLOB,
                SEVERITY LONGBLOB,
                ORTHOCHECK LONGBLOB
            )
            """)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database setup error: {e}")
        return False


# Authentication functions
def read_credentials():
    patients = {}
    admins = {}

    try:
        with open("credentials/patients.txt", "r") as f:
            content = f.readlines()
            for line in content:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        patients[parts[0]] = parts[1]
    except Exception as e:
        st.warning(f"Could not read patient credentials: {e}")

    try:
        with open("credentials/admins.txt", "r") as f:
            content = f.readlines()
            for line in content:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        admins[parts[0]] = parts[1]
    except Exception as e:
        st.warning(f"Could not read admin credentials: {e}")

    return patients, admins


def patient_login(phone, password):
    patients, _ = read_credentials()

    if phone not in patients:
        st.error("No account found with this phone number. Please sign up.")
        return False

    if patients[phone] != password:
        st.error("Incorrect password!")
        return False

    st.session_state.user_id = phone
    st.session_state.role = 'patient'
    st.session_state.current_page = 'patient_dashboard'
    return True


def patient_signup(phone, password):
    patients, _ = read_credentials()

    if phone in patients:
        st.error("Account already exists! Please login.")
        return False

    if " " in password:
        st.error("Password cannot contain spaces.")
        return False

    with open("credentials/patients.txt", "a") as f:
        f.write(f"{phone},{password}\n")

    st.success("Account created successfully! Please login.")
    return True


def admin_login(admin_id, password):
    _, admins = read_credentials()

    if admin_id not in admins:
        st.error("Admin ID not found.")
        return False

    if admins[admin_id] != password:
        st.error("Incorrect password!")
        return False

    st.session_state.user_id = admin_id
    st.session_state.role = 'admin'
    st.session_state.current_page = 'admin_dashboard'
    return True


def admin_signup(admin_id, password):
    _, admins = read_credentials()

    if admin_id in admins:
        st.error("Admin ID already exists.")
        return False

    if " " in admin_id or " " in password:
        st.error("Admin ID and password cannot contain spaces.")
        return False

    with open("credentials/admins.txt", "a") as f:
        f.write(f"{admin_id},{password}\n")

    st.success("Admin account created successfully! Please login.")
    return True


# Patient data processing functions
def extract_full_name(user_input):
    phrases = ["my name is", "call me", "it's", "it is", "i am", "i'm", "name's", "they call me"]
    user_input = user_input.strip().lower()

    for phrase in phrases:
        if phrase in user_input:
            name_part = user_input.split(phrase, 1)[1].strip()
            full_name = re.sub(r'[^\w\s]', '', name_part)
            return full_name.title()

    if re.match(r'^[a-zA-Z\s]+$', user_input):
        return user_input.title()

    return None


def extract_age(text):
    try:
        with open('a2.json', 'r') as f:
            age_data = json.load(f)

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
    except Exception as e:
        st.error(f"Error extracting age: {e}")
        return None


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

    return "Unrecognized"


def check_medical_history(user_input, yn):
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

    while yn.lower() not in ["yes", "no"]:
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


def fetch_symptoms(user_input):
    # Simplified version that checks for common symptoms

    user_input_lower = user_input.lower()

    try:
        response = model.generate_content(
            f"what are all the symptoms from the following prompt, if the prompt mentions pain, include the areas of pain in the response as 'pain in and body part name' (just the words) else return None:{user_input}")
        symptoms = [x.strip() for x in response.text.split(",")]
        if symptoms[0] == None:
            return []
        return symptoms
    except Exception as e:
        return

def check_ortho_symptoms(symptoms, diseases):
    # Simplified orthopedic check based on symptoms and diseases
    ortho_symptoms = ["back pain", "joint pain", "pain in arms", "pain in legs", "swelling"]
    ortho_diseases = ["arthritis", "osteoporosis"]

    if any(symptom in ortho_symptoms for symptom in symptoms):
        return True

    if diseases and any(disease in ortho_diseases for disease in diseases):
        return True

    return False


# Data encryption functions
def encrypt_data(patient_data):
    enckey = Fernet.generate_key()
    cipher_suite = Fernet(enckey)

    encrypted_data = {}
    for key, value in patient_data.items():
        if key == "phone" or value is None:
            encrypted_data[key] = value
            continue

        # Convert to string and then to bytes before encrypting
        encoded_text = cipher_suite.encrypt(str(value).encode('utf-8'))
        encrypted_data[key] = encoded_text

    # Save the key with timestamp and phone number
    dt = datetime.now()
    date_str = dt.strftime("%Y%m%d")
    time_str = dt.strftime("%H%M%S")

    with open("keymap.txt", "a") as f:
        f.write(f"{date_str},{time_str},{patient_data['phone']},{enckey.decode('utf-8')}\n")

    return encrypted_data, enckey


def store_data(data):
    try:
        conn = pymysql.connect(host="localhost", user="root", password="password")
        cursor = conn.cursor()
        cursor.execute("USE MODULE3")

        query = "INSERT INTO DATA VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            data["phone"],
            data["name"],
            data["age"],
            data["gender"],
            data["diseases"],
            data["symptoms"],
            data["frequency"],
            data["duration"],
            data["severity"],
            data["orthoCheck"]
        )

        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error storing data: {e}")
        return False


def fetch_data(key, phone):
    try:
        conn = pymysql.connect(host="localhost", user="root", password="password")
        cursor = conn.cursor()
        cursor.execute("USE MODULE3")

        query = 'SHOW COLUMNS FROM DATA'
        cursor.execute(query)
        ans = cursor.fetchall()
        column_names = [column[0].capitalize() for column in ans]

        cipher_suite = Fernet(key)

        query = "SELECT * FROM DATA WHERE phone = %s"
        cursor.execute(query, (phone,))
        records = cursor.fetchall()

        if not records:
            return None

        patient_records = []
        for record in records:
            try:
                patient_record = {}
                for i in range(len(record)):
                    if i == 0:  # Phone is not encrypted
                        patient_record[column_names[i]] = record[i]
                    else:
                        decrypted_value = cipher_suite.decrypt(record[i]).decode('utf-8')
                        patient_record[column_names[i]] = decrypted_value

                patient_records.append(patient_record)
            except Exception:
                continue

        return patient_records
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def update_patient_data(key, phone, new_data):
    try:
        cipher_suite = Fernet(key)

        encrypted_data = {}
        for key_name, value in new_data.items():
            if key_name.lower() == "phone":
                encrypted_data[key_name.lower()] = value
                continue

            encoded_text = cipher_suite.encrypt(str(value).encode('utf-8'))
            encrypted_data[key_name.lower()] = encoded_text

        conn = pymysql.connect(host="localhost", user="root", password="password")
        cursor = conn.cursor()
        cursor.execute("USE MODULE3")

        query = "UPDATE DATA SET PHONE = %s, NAME = %s, AGE = %s, GENDER = %s WHERE PHONE = %s"
        values = (
            new_data["phone"],
            encrypted_data["name"],
            encrypted_data["age"],
            encrypted_data["gender"],
            phone
        )

        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating data: {e}")
        return False


# Report generation
def generate_report(patient_data):
    report = f"""
    MEDICAL ASSESSMENT REPORT

    PATIENT INFORMATION:
    ------------------------
    Name: {patient_data['name']}
    Age: {patient_data['age']}
    Gender: {patient_data['gender']}

    MEDICAL ASSESSMENT:
    ------------------------
    Reported Symptoms: {patient_data['symptoms']}
    Symptom Frequency: {patient_data['frequency']}
    Duration: {patient_data['duration']}
    Severity (1-10): {patient_data['severity']}

    Existing Conditions: {patient_data['diseases'] if patient_data['diseases'] else "None reported"}

    RECOMMENDATION:
    ------------------------
    Based on the assessment, the patient {
    "should consult with an orthopedic specialist."
    if patient_data['orthoCheck'] == 'True' else
    "does not require immediate orthopedic consultation."
    }

    Please note this is an automated screening assessment and not a definitive diagnosis.
    Follow-up with appropriate healthcare providers is recommended.

    Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """

    return report


def get_pdf_download_link(report_text, filename="patient_report.txt"):
    """Generate a download link for the report"""
    b64 = base64.b64encode(report_text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}">Download Report</a>'


# Text-to-speech function
async def text_to_speech(text, lang_code='en'):
    try:
        voice = languages[lang_code]['voice']

        output_file = "temp_audio.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        with open(output_file, "rb") as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format="audio/mp3")

        await asyncio.sleep(0.5)
        # Cleanup
        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")


# UI Components
def login_page():
    st.title("OrthoCheck Medical Assistant")

    tab1, tab2, tab3, tab4 = st.tabs(["Patient Login", "Patient Signup", "Admin Login", "Admin Signup"])

    with tab1:
        st.header("Patient Login")
        phone = st.text_input("Phone Number", key="patient_login_phone")
        password = st.text_input("Password", type="password", key="patient_login_password")

        if st.button("Login", key="patient_login_button"):
            if len(phone) < 10 or not phone[-10:].isdigit():
                st.error("Please enter a valid 10-digit phone number.")
            else:
                phone = phone[-10:]
                if patient_login(phone, password):
                    st.success("Login successful!")
                    st.rerun()

    with tab2:
        st.header("Patient Signup")
        phone = st.text_input("Phone Number", key="patient_signup_phone")
        password = st.text_input("Password", type="password", key="patient_signup_password")

        if st.button("Sign Up", key="patient_signup_button"):
            if len(phone) < 10 or not phone[-10:].isdigit():
                st.error("Please enter a valid 10-digit phone number.")
            else:
                phone = phone[-10:]
                if patient_signup(phone, password):
                    st.success("Signup successful! Please log in.")

    with tab3:
        st.header("Admin Login")
        admin_id = st.text_input("Admin ID", key="admin_login_id")
        password = st.text_input("Password", type="password", key="admin_login_password")

        if st.button("Login", key="admin_login_button"):
            if admin_login(admin_id, password):
                st.success("Login successful!")
                st.rerun()

    with tab4:
        st.header("Admin Signup")
        admin_id = st.text_input("Admin ID", key="admin_signup_id")
        password = st.text_input("Password", type="password", key="admin_signup_password")

        if st.button("Sign Up", key="admin_signup_button"):
            if admin_signup(admin_id, password):
                st.success("Signup successful! Please log in.")


def patient_dashboard():
    st.title(f"Welcome to OrthoCheck")
    st.subheader("Patient Dashboard")

    tab1, tab2 = st.tabs(["New Assessment", "View Records"])

    with tab1:
        st.header("Start New Assessment")
        language_option = st.selectbox(
            "Select Language",
            options=["English", "Hindi", "French", "German"],
            index=0
        )

        lang_mapping = {"English": "en", "Hindi": "hindi", "French": "fr", "German": "de"}
        selected_lang = lang_mapping[language_option]
        st.session_state.lang = selected_lang

        interaction_option = st.radio(
            "Select Interaction Type",
            options=["Text-based", "Voice-based"],
            index=0
        )

        if st.button("Start Assessment"):
            st.session_state.current_page = 'assessment'
            st.session_state.interaction_type = "1" if interaction_option == "Text-based" else "2"
            st.rerun()

    with tab2:
        st.header("View Your Records")

        st.info(
            "To view your encrypted records, you need the encryption key that was provided when you created the record.")

        key_input = st.text_input("Enter your encryption key:", type="password")

        if st.button("Fetch Records") and key_input:
            try:
                # Convert string key to bytes
                key_bytes = key_input.encode('utf-8')
                records = fetch_data(key_bytes, st.session_state.user_id)

                if records:
                    st.success("Records found!")
                    st.session_state.reports = records

                    for i, record in enumerate(records):
                        with st.expander(f"Record {i + 1}"):
                            for key, value in record.items():
                                st.text(f"{key}: {value}")

                            report_text = generate_report(record)
                            st.markdown("### Report")
                            st.text(report_text)

                            st.markdown(get_pdf_download_link(report_text, f"patient_report_{i + 1}.txt"),
                                        unsafe_allow_html=True)
                else:
                    st.error("No records found or incorrect encryption key.")
            except Exception as e:
                st.error(f"Error: {e}")
                st.error("Could not decrypt records with the provided key.")

    if st.button("Logout"):
        st.session_state.current_page = 'login'
        st.session_state.role = None
        st.session_state.user_id = None
        st.rerun()


def admin_dashboard():
    st.title("OrthoCheck Admin Dashboard")

    tab1, tab2 = st.tabs(["View Patient Data", "Update Patient Records"])

    with tab1:
        st.header("View Patient Data")

        phone = st.text_input("Patient Phone Number")
        key_input = st.text_input("Encryption Key", type="password")

        if st.button("Fetch Patient Data") and phone and key_input:
            try:
                key_bytes = key_input.encode('utf-8')
                records = fetch_data(key_bytes, phone)

                if records:
                    st.success("Patient records found!")

                    for i, record in enumerate(records):
                        with st.expander(f"Record {i + 1}"):
                            for key, value in record.items():
                                st.text(f"{key}: {value}")

                            report_text = generate_report(record)
                            st.markdown("### Report")
                            st.text(report_text)

                            st.markdown(get_pdf_download_link(report_text, f"patient_report_{phone}_{i + 1}.txt"),
                                        unsafe_allow_html=True)
                else:
                    st.error("No records found or incorrect encryption key.")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.header("Update Patient Record")

        phone = st.text_input("Patient Phone Number", key="update_phone")
        key_input = st.text_input("Encryption Key", type="password", key="update_key")

        if st.button("Verify Patient") and phone and key_input:
            try:
                key_bytes = key_input.encode('utf-8')
                records = fetch_data(key_bytes, phone)

                if records:
                    st.session_state.update_record = records[0]
                    st.session_state.key = key_bytes
                    st.success("Patient verified! Update the information below.")

                    # Create form for updating
                    with st.form("update_form"):
                        new_phone = st.text_input("New Phone Number", value=phone)
                        new_name = st.text_input("New Name", value=records[0]['Name'])
                        new_age = st.text_input("New Age", value=records[0]['Age'])
                        new_gender = st.selectbox(
                            "New Gender",
                            options=["Male", "Female", "Non-Binary", "Prefer Not to Say"],
                            index=["Male", "Female", "Non-Binary", "Prefer Not to Say"].index(records[0]['Gender'])
                            if records[0]['Gender'] in ["Male", "Female", "Non-Binary", "Prefer Not to Say"] else 0
                        )

                        if st.form_submit_button("Update Record"):
                            new_data = {
                                "phone": new_phone,
                                "name": new_name,
                                "age": new_age,
                                "gender": new_gender
                            }

                            if update_patient_data(key_bytes, phone, new_data):
                                st.success("Record updated successfully!")
                            else:
                                st.error("Failed to update record.")
                else:
                    st.error("No records found or incorrect encryption key.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Logout"):
        st.session_state.current_page = 'login'
        st.session_state.role = None
        st.session_state.user_id = None
        st.rerun()


def assessment_page():
    st.title("Medical Assessment")

    if 'assessment_step' not in st.session_state:
        st.session_state.assessment_step = 1
        st.session_state.patient_data = {
            "phone": st.session_state.user_id
        }

    # TTS function for assessment
    def play_tts(text):
        if st.session_state.interaction_type == "2":  # Voice-based
            st.text("🔊 Playing audio...")
            asyncio.run(text_to_speech(text, st.session_state.lang))

    # Step 1: Name
    if st.session_state.assessment_step == 1:
        st.header("Step 1: Personal Information")

        prompt_text = "What is your name?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        name_input = st.text_input("Your response:", key="name_input")

        if st.button("Next", key="name_next"):
            if name_input:
                name = extract_full_name(name_input) or name_input
                st.session_state.patient_data["name"] = name
                st.session_state.assessment_step = 2
                st.rerun()
            else:
                st.error("Please enter your name.")

    # Step 2: Age
    elif st.session_state.assessment_step == 2:
        st.header("Step 2: Age")

        prompt_text = "What is your age?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        age_input = st.text_input("Your response:", key="age_input")

        if st.button("Next", key="age_next"):
            if age_input:
                age = extract_age(age_input) or age_input
                st.session_state.patient_data["age"] = age
                st.session_state.assessment_step = 3
                st.rerun()
            else:
                st.error("Please enter your age.")

    # Step 3: Gender
    elif st.session_state.assessment_step == 3:
        st.header("Step 3: Gender")

        prompt_text = "What is your gender?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        gender_options = ["Male", "Female", "Non-Binary", "Prefer Not to Say"]
        gender_input = st.selectbox("Select your gender:", gender_options)

        if st.button("Next", key="gender_next"):
            st.session_state.patient_data["gender"] = gender_input
            st.session_state.assessment_step = 4
            st.rerun()

    # Step 4: Medical History
    elif st.session_state.assessment_step == 4:
        st.header("Step 4: Medical History")

        prompt_text = "Do you have any existing medical conditions?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        has_conditions = st.radio("", ["Yes", "No"], index=1)

        if has_conditions == "Yes":
            conditions_input = st.text_area("Please list your medical conditions:")

            if st.button("Next", key="conditions_next"):
                if conditions_input:
                    conditions = check_medical_history(conditions_input, has_conditions)
                    conditions_str = ", ".join(conditions) if conditions else "None specified"
                    st.session_state.patient_data["diseases"] = conditions_str
                else:
                    st.session_state.patient_data["diseases"] = "None specified"

                st.session_state.assessment_step = 5
                st.rerun()
        else:
            if st.button("Next", key="no_conditions_next"):
                st.session_state.patient_data["diseases"] = "None"
                st.session_state.assessment_step = 5
                st.rerun()

    # Step 5: Symptoms
    elif st.session_state.assessment_step == 5:
        st.header("Step 5: Symptoms")

        prompt_text = "Please describe your symptoms in detail."
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        symptoms_input = st.text_area("Your symptoms:", key="symptoms_input")

        if st.button("Next", key="symptoms_next"):
            if symptoms_input:
                detected_symptoms = fetch_symptoms(symptoms_input)
                symptoms_str = ", ".join(detected_symptoms)
                st.session_state.patient_data["symptoms"] = symptoms_str
                st.session_state.assessment_step = 6
                st.rerun()
            else:
                st.error("Please describe your symptoms.")

        # Step 6: Symptom Frequency
    elif st.session_state.assessment_step == 6:
        st.header("Step 6: Symptom Frequency")

        prompt_text = "How often do you experience these symptoms?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        frequency_options = ["Constantly", "Several times a day", "Daily", "A few times a week", "Weekly", "Monthly",
                             "Rarely"]
        frequency_input = st.selectbox("Select frequency:", frequency_options)

        if st.button("Next", key="frequency_next"):
            st.session_state.patient_data["frequency"] = frequency_input
            st.session_state.assessment_step = 7
            st.rerun()

        # Step 7: Duration
    elif st.session_state.assessment_step == 7:
        st.header("Step 7: Symptom Duration")

        prompt_text = "How long have you been experiencing these symptoms?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        duration_options = ["Less than a day", "A few days", "A week", "Several weeks", "A month", "Several months",
                            "More than a year"]
        duration_input = st.selectbox("Select duration:", duration_options)

        if st.button("Next", key="duration_next"):
            st.session_state.patient_data["duration"] = duration_input
            st.session_state.assessment_step = 8
            st.rerun()

        # Step 8: Severity
    elif st.session_state.assessment_step == 8:
        st.header("Step 8: Symptom Severity")

        prompt_text = "On a scale of 1 to 10, how would you rate the severity of your symptoms?"
        st.text(f"Assistant: {prompt_text}")
        play_tts(prompt_text)

        severity_input = st.slider("Severity (1-10):", 1, 10, 5)

        if st.button("Complete Assessment", key="severity_next"):
            st.session_state.patient_data["severity"] = str(severity_input)

            # Determine if orthopedic check is needed
            diseases = st.session_state.patient_data.get("diseases", "").split(", ")
            symptoms = st.session_state.patient_data.get("symptoms", "").split(", ")
            ortho_check = check_ortho_symptoms(symptoms, diseases)
            st.session_state.patient_data["orthoCheck"] = str(ortho_check)

            # Encrypt and store the data
            encrypted_data, key = encrypt_data(st.session_state.patient_data)

            if store_data(encrypted_data):
                st.session_state.key = key
                st.session_state.assessment_step = 9
                st.rerun()
            else:
                st.error("Failed to save your assessment. Please try again.")

        # Step 9: Results
    elif st.session_state.assessment_step == 9:
        st.header("Assessment Complete")

        st.success("Your assessment has been successfully completed and stored!")

        st.subheader("Assessment Summary")
        for key, value in st.session_state.patient_data.items():
            if key != "phone":
                st.text(f"{key.capitalize()}: {value}")

        report_text = generate_report(st.session_state.patient_data)
        st.markdown("### Your Medical Report")
        st.text_area("Report", report_text, height=300)

        st.markdown(get_pdf_download_link(report_text, "orthocheck_report.txt"), unsafe_allow_html=True)

        # Display encryption key for future access
        st.warning("IMPORTANT: Save your encryption key to access your record in the future.")
        st.code(st.session_state.key.decode('utf-8'))

        if st.button("Return to Dashboard"):
            st.session_state.assessment_step = 1
            st.session_state.current_page = 'patient_dashboard'
            st.rerun()

        # Back button for navigation
    if st.session_state.assessment_step > 1 and st.session_state.assessment_step < 9:
        if st.button("Back"):
            st.session_state.assessment_step -= 1
            st.rerun()

    # Main app logic
def main():
    # Setup database if not already set up
    setup_database()

    # Navigation based on session state
    if st.session_state.current_page == 'login':
        login_page()
    elif st.session_state.current_page == 'patient_dashboard':
        patient_dashboard()
    elif st.session_state.current_page == 'admin_dashboard':
        admin_dashboard()
    elif st.session_state.current_page == 'assessment':
        assessment_page()
    else:
        st.session_state.current_page = 'login'
        st.rerun()

if __name__ == "__main__":
    configureLLM()
    main()