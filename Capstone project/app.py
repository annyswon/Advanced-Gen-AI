import streamlit as st
import pandas as pd
import PyPDF2
import os

DATA_DIR = "data"
TICKET_FILE = "tickets.csv"

# Load docs
def load_pdfs():
    docs = {}
    for fname in os.listdir(DATA_DIR):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, fname)
            reader = PyPDF2.PdfReader(path)
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append((i+1, text))
            docs[fname] = pages
    return docs

def load_texts():
    texts = {}
    for fname in os.listdir(DATA_DIR):
        if fname.lower().endswith((".txt", ".md")):
            path = os.path.join(DATA_DIR, fname)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                texts[fname] = f.read()
    return texts

pdf_docs = load_pdfs()
text_docs = load_texts()

# Simple search (naive keyword match)
def search_docs(query):
    results = []
    for fname, pages in pdf_docs.items():
        for page_num, text in pages:
            if query.lower() in text.lower():
                results.append((fname, page_num, text[:300]))
    for fname, text in text_docs.items():
        if query.lower() in text.lower():
            results.append((fname, None, text[:300]))
    return results

# Ticket system
def create_ticket(name, email, summary, description):
    new_ticket = {
        "name": name,
        "email": email,
        "summary": summary,
        "description": description
    }
    if os.path.exists(TICKET_FILE):
        df = pd.read_csv(TICKET_FILE)
    else:
        df = pd.DataFrame(columns=["name", "email", "summary", "description"])
    df = pd.concat([df, pd.DataFrame([new_ticket])], ignore_index=True)
    df.to_csv(TICKET_FILE, index=False)

# ---- Streamlit UI ----
st.title("💬 Customer Support Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.history.append(("user", user_input))
    results = search_docs(user_input)
    if results:
        answer = "I found some info:\n"
        for r in results[:2]:
            source = f"{r[0]} p.{r[1]}" if r[1] else r[0]
            answer += f"- **{source}** → {r[2]}...\n"
    else:
        answer = "I couldn’t find an answer. Would you like to create a support ticket?"
        st.session_state.pending_ticket = user_input
    st.session_state.history.append(("bot", answer))

# Show chat history
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

# Ticket form if needed
if "pending_ticket" in st.session_state:
    st.divider()
    st.subheader("Create Support Ticket")
    with st.form("ticket_form"):
        name = st.text_input("Your name")
        email = st.text_input("Your email")
        summary = st.text_input("Summary", st.session_state.pending_ticket[:50])
        desc = st.text_area("Description", st.session_state.pending_ticket)
        submit = st.form_submit_button("Submit")
        if submit:
            create_ticket(name, email, summary, desc)
            st.success("✅ Ticket created successfully!")
            del st.session_state.pending_ticket
