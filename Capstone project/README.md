# Capstone Project – Customer Support Chatbot

## Objective
Build a customer support solution that:
- Lets users ask questions via a web chat.
- Answers from internal documents (PDFs + text files).
- Always cites the **document and page** when giving an answer.
- Suggests creating a **support ticket** if no answer is found.
- Allows users to create a ticket with:
  - Name
  - Email
  - Summary
  - Description  
- Stores support tickets in a CSV file (simple issue tracking).
- Keeps **conversation history** in the chat.
- Knows the company info (from `company_info.md`).

## Data sources
- At least **3 documents**:
  - 2 PDFs (including 1 large 400+ pages PDF)
  - 1 Markdown file (`company_info.md`)
- Example setup:
  - `long_manual.pdf` (400+ pages, e.g., PostgreSQL manual)
  - `product_guide.pdf` (smaller reference doc)
  - `company_info.md` (company details: name, email, phone)

## Technical requirements
- **Python** with dependencies listed in `requirements.txt`.
- **Streamlit** for the Web UI.
- **PyPDF2** for PDF parsing.
- **Pandas** for storing support tickets.
- **Deployment**: Hugging Face Spaces (Streamlit app).

## Running locally
```bash
pip install -r requirements.txt
streamlit run app.py

