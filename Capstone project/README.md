# Customer Support Chatbot

## What was done
Built a customer support chatbot using **Streamlit**.  
Connected it to documents with **RAG (Retrieval-Augmented Generation)**.  
Added **citations** (file + page) in answers.  
If no answer is found → suggests creating a **GitHub support ticket**.  
Tickets include:
- User name & email
- Summary + description
- Original user query
- Auto-label: `support`

---
## What to improve
Work on the replies (imrove research ingine)== Use a stronger embedding model for better search.  
Add more ticket integrations (Jira, Trello).  
Add multi-language support.  
Store chat history in a database.  
Build a small dashboard for tickets/analytics.  

## Files
- `app.py` – main Streamlit app  
- `tickets.py` – GitHub issue creation  
- `requirements.txt` – dependencies  
- `runtime.txt` – Python version   
- `data/` – folder with documents (PDF + TXT)  

## Screenshots

### 1. Main Interface
![Main UI](screenshots/photo_2025-09-04%2002.33.30.jpeg)

### 2. Asking a Question
![Answer with Sources](screenshots/photo_2025-09-04%2002.33.38.jpeg)

### 3. Ticket Form
![Create Ticket Form](screenshots/photo_2025-09-04%2002.33.49.jpeg)

### 4. Ticket Submission
![Ticket Created](screenshots/photo_2025-09-04%2002.34.00.jpeg)

### 5. GitHub Issue Example
![GitHub Issue](screenshots/photo_2025-09-04%2002.34.05.jpeg)

### 6. GitHub Issues List
![GitHub Issues List](screenshots/photo_2025-09-04%2002.34.10.jpeg)




