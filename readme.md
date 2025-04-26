# OrthoCheck Medical Assistant

OrthoCheck is a Streamlit-based web application designed to provide medical assessments with a focus on orthopedic symptom detection. This interactive medical assistant guides users through a comprehensive assessment process, securely stores their data, and provides reports with recommendations.

## Features

- **Multi-language Support**: Interface available in English, Hindi, French, and German with text-to-speech capabilities
- **Secure Authentication**: Separate login systems for patients and administrators
- **Comprehensive Assessment**: Guided step-by-step symptom and medical history collection
- **Automated Analysis**: Identification of potential orthopedic concerns
- **End-to-end Encryption**: Patient data is encrypted for privacy protection
- **Report Generation**: Detailed medical assessment reports available for download
- **Admin Dashboard**: Administrative tools for viewing and updating patient records

## Requirements

- Python 3.8 or higher
- MySQL Server
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DarshanBothra/AIIMSD-Chatbot.git
   cd AIIMSD-Chatbot
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL database**
   - Ensure MySQL server is running
   - Default configuration in the app:
     - Host: localhost
     - User: root
     - Password: password
   - The application will automatically create the required database and tables

5. **Configure Google Gemini API**
   - Obtain an API key from Google AI Studio
   - The API key should be in the `apikey.txt` file

## Running the Application

To run the OrthoCheck Medical Assistant, make sure your virtual environment is activated and execute:

```bash
streamlit run Frontend/main.py
```

This command starts the Streamlit server and launches the application. By default, Streamlit will:
- Start a local development server
- Open your default web browser to http://localhost:8501
- Display the OrthoCheck interface

If the browser doesn't open automatically, manually navigate to http://localhost:8501.

To stop the application, press `Ctrl+C` in the terminal where Streamlit is running.

### Running on a Different Port

If port 8501 is already in use, you can specify a different port:

```bash
streamlit run Frontend/main.py --server.port 8502
```

### Running in Headless Mode

To run the application without automatically opening a browser:

```bash
streamlit run Frontend/main.py --server.headless true
```

## Usage

### Patient Workflow

1. **Login/Sign Up**
   - New patients can create an account using a phone number and password
   - Returning patients can log in with their credentials

2. **Start an Assessment**
   - Choose your preferred language
   - Select interaction type (text-based or voice-based)
   - Follow the step-by-step assessment process

3. **Review and Access Records**
   - After completing an assessment, save your encryption key
   - Use this key to access your medical records and reports in the future

### Admin Workflow

1. **Login/Sign Up**
   - Administrators can access the system with admin credentials
   - Default admin credentials: admin/admin123

2. **View Patient Data**
   - Search for patient records using phone number and encryption key
   - View detailed patient information and medical assessment reports

3. **Update Patient Records**
   - Modify patient information when necessary
   - Ensure data accuracy and completeness

## Project Structure

- `main.py`: The main application file containing the Streamlit interface and core functionality
- `pdf_gen.py`: Module for generating PDF reports
- `requirements.txt`: List of Python dependencies
- `apikey.txt`: Google Gemini API key for NLP processing
- `credentials/`: Directory for storing user credentials
- `data/`: Directory for application data storage
- `reports/`: Directory for generated reports

## Security Features

- End-to-end encryption for patient medical data
- Secure authentication system
- Encryption keys provided to patients for record access
- Database security through encryption of sensitive fields

## Customization

### Modifying the Database Configuration

To change the database connection parameters, locate these lines in `main.py`:

```python
conn = pymysql.connect(host="localhost", user="root", password="password")
```

Update the values to match your MySQL configuration.

### Adding Languages

To add support for additional languages, modify the `languages` dictionary in `main.py`:

```python
languages = {
    "en": {"code": "en", "name": "English", "voice": "en-US-JennyNeural"},
    # Add new languages here
}
```

## Troubleshooting

- **Database Connection Issues**: Ensure MySQL server is running and credentials are correct
- **Text-to-Speech Not Working**: Check that edge-tts is properly installed
- **Missing Reports**: Verify the 'reports' directory exists and has proper permissions
- **Streamlit Errors**: If you encounter Streamlit-related errors, try clearing the cache with `streamlit cache clear` and restart the application

## License

[Add your license information here]

## Acknowledgements

- This project uses the Gemini API from Google for natural language processing
- Edge TTS is used for text-to-speech capabilities

---

For questions or support, please [contact information or issue reporting guidelines]
