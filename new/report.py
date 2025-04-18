import chatbot3
import ollama
import pdf_gen

def language_prefer()->str:
    inp=input("Enter 1-for englsh , 2.-Hindi, 3.-french, 4.-german\nEnter Preference: ")
    var=""
    if inp=='1':
        var="en"
    elif inp=='2':
        var="hindi"
    elif inp=='3':
        var="fr"
    elif inp=='4':
        var='german'
    else:
        print("Enter valid choice:")
        return language_prefer()
    return var
var=language_prefer()
# global interaction_type
# interaction_type = chatbot3.getInteractionType()
chatbot3.configureLLM()
chatbot3.greet(var)
patient_data = chatbot3.getPatientData(var)

response = ollama.chat(
    model = 'deepseek-r1:7b',
    messages = [
        {

        'role': 'user',
        'content': f"Summarize this patient's report for a doctor. Use plain language. Do not include the name, age, or gender of the patient in the report. The report must be in 60-80 words, the patient is to been consulted with an orthopedic doctor (donot mention orthoCheck in the response), mention that in the report too. Data: {patient_data}"
    }
    ]
)

       

report = f"""
        Name: {patient_data['name']}
        Age: {patient_data['age']}
        Gender: {patient_data['gender']}
        
        {response['message']['content']}
        
        """


report = report[0: report.index("<think>")] + report[report.index("</think>")+8: ]
print(report)

pdf_gen.generate_pdf(patient_data,report)
