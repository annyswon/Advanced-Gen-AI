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





