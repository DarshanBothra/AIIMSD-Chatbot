import chatbot
import ollama
import store_data

chatbot.configureLLM()
chatbot.greet()
patient_data = chatbot.getPatientData()
store_data.store_data(*list(patient_data.values()))

response = ollama.chat(
    model = 'deepseek-r1:7b',
    messages = [
        {

        'role': 'user',
        'content': f"Summarize this patient's report for a doctor. Use plain language. Do not include the name, age, or gender of the patient in the report. The report must not be greater than 100 words if orthoCheck is confirmed, the patient is to been consulted with an orthopedic doctor (donot mention orthoCheck in the response), mention that in the report too. Data: {patient_data}"
    }
    ]
)

report = f"""
        Name: {patient_data['name']}
        Age: {patient_data['age']}
        Gender: {patient_data['gender']}
        
        {response['message']['content']}
        
        """

print(report[0: report.index("<think>")], report[report.index("</think>")+8: ])