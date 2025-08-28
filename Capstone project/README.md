# Capstone Project – Customer Support Chatbot

## Objective
The objective of this project is to build a customer support solution that can answer user questions from internal documents and, if an answer is not found, allow the user to create a support ticket. The system is designed to run locally or in a deployed environment such as Hugging Face Spaces using Streamlit.

---

## Business Features
- Web-based chat where users can ask questions and receive answers from company documents.  
- Answers are always cited with the document name and page number.  
- If no answer is found, the system suggests creating a support ticket.  
- Users can create a support ticket by providing their name, email, a summary (title), and a detailed description.  
- Support tickets are stored in a CSV file, serving as a simple issue tracker.  
- Conversation history is preserved within the session, so the system keeps context.  
- The AI has access to company information such as name, email, and phone number from `company_info.md`.

---

## Data Sources
At least three documents are used as knowledge sources:

1. **Ford-F-150-Owners-Manual.pdf**  
   - PDF document, over 400 pages  
   - Satisfies the requirement for one large document  

2. **porsche-2017-macan-Owners-Manual.pdf**  
   - PDF document, ~150 pages  
   - Serves as a second supporting PDF  

3. **company_info.md**  
   - Markdown document containing company details such as contact information  

(Optional) An additional `faq.txt` file can be included with common questions and answers for faster responses.

---

## Technical Requirements
- Implemented in **Python**  
- Dependencies listed in `requirements.txt`  
- Python version specified in `runtime.txt`  
- Document parsing uses `PyPDF2`  
- Ticket storage uses `pandas`  
- Web interface built with **Streamlit**  
- Deployable to Hugging Face Spaces

---

## Running Locally
1. Clone the repository and navigate into the project folder.  
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
