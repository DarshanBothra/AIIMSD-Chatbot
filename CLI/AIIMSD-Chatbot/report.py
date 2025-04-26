"""
THis module used deepseek-r1:7b model. Please install the model via ollama on your local runtime before using the program.
"""

import chatbot2
import ollama
import pdf_gen

chatbot2.configureLLM()
chatbot2.greet()
patient_data = chatbot2.getPatientData()

response = ollama.chat(
    model = 'deepseek-r1:7b',
    messages = [
        {

        'role': 'user',
        'content': f"Summarize this patient's report for a doctor. Use plain language. Do not include the name, age, or gender of the patient in the report. The report must be in 60-80 words, the patient is to been consulted with an orthopedic doctor (donot mention orthoCheck in the response), mention that in the report too. Data: {patient_data}"
    }
    ]
)

if patient_data['name'] and patient_data['symptoms']:

    report = f"""
            Name: {patient_data['name']}
            Age: {patient_data['age']}
            Gender: {patient_data['gender']}
            
            {response['message']['content']}
            
            """

    print(report[0: report.index("<think>")], report[report.index("</think>")+8: ])

    pdf_gen.generate_pdf(patient_data,report)
else:
    print("Data could not be obtained... report cannot be generated!")
