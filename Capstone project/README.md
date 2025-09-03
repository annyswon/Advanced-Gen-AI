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

## Files
- `app.py` – main Streamlit app  
- `tickets.py` – GitHub issue creation  
- `requirements.txt` – dependencies  
- `runtime.txt` – Python version   
- `data/` – folder with documents (PDF + TXT)  

---

## How to install and run
1. Clone the repo:
   ```bash
   git clone https://github.com/annyswon/Advanced-Gen-AI.git
   cd Advanced-Gen-AI
   
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Put your documents in the data/ folder (at least 3 docs, 2 PDFs, one large PDF).
5. Run the app:
   ```bash
   streamlit run app.py

## What to improve
Work on the replies (imrove research ingine).  
Add more ticket integrations (Jira, Trello).  
Use a stronger embedding model for better search.  
Add multi-language support.  
Store chat history in a database.  
Build a small dashboard for tickets/analytics.  

## Screenshots

## Screenshots

Here are some screenshots showing how the Customer Support Chat (RAG + GitHub Tickets) works:

### Main Interface
![Main UI](./screenshots/photo_2025-09-04_02.33.30.jpeg)

### Asking a Question
![Answer with Sources](./screenshots/photo_2025-09-04_02.33.38.jpeg)

### Ticket Form
![Create Ticket Form](./screenshots/photo_2025-09-04_02.33.49.jpeg)

### Ticket Submission
![Ticket Created](./screenshots/photo_2025-09-04_02.34.00.jpeg)

### GitHub Issue Example
![GitHub Issue](./screenshots/photo_2025-09-04_02.34.05.jpeg)

### GitHub Issues List
![GitHub Issues List](./screenshots/photo_2025-09-04_02.34.10.jpeg)


