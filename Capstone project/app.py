# --- Make Streamlit write to a writable path on HF Spaces ---
import os
os.environ["STREAMLIT_GLOBAL_DATA_DIR"] = "/tmp/.streamlit"
os.environ["XDG_CACHE_HOME"] = "/tmp"
os.environ["STREAMLIT_CACHE_DIR"] = "/tmp/streamlit-cache"
os.makedirs("/tmp/.streamlit", exist_ok=True)
os.makedirs("/tmp/streamlit-cache", exist_ok=True)

import re
import pandas as pd
import streamlit as st
import PyPDF2

# ---- Paths ----
DATA_DIR = "data"                # your repo's data folder (read-only on Spaces)
TICKET_FILE = "/tmp/tickets.csv" # writable on Spaces

# ---- Helpers ----
def _excerpt(text: str, query: str, window: int = 280) -> str:
    """Return a short excerpt around the first match of query."""
    if not text:
        return ""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        return text[:window].strip().replace("\n", " ")
    start = max(0, m.start() - window // 2)
    end = min(len(text), m.end() + window // 2)
    snippet = text[start:end].strip().replace("\n", " ")
    return snippet

@st.cache_resource(show_spinner=False)
def load_pdfs():
    """Load all PDFs from data/ into memory as {filename: [(page, text), ...]}."""
    docs = {}
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, fname)
            try:
                reader = PyPDF2.PdfReader(path)
            except Exception as e:
                st.warning(f"Could not open {fname}: {e}")
                continue
            pages = []
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                pages.append((i + 1, text))
            docs[fname] = pages
    return docs

@st.cache_resource(show_spinner=False)
def load_texts():
    """Load .txt/.md files from data/ into memory as {filename: text}."""
    out = {}
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.lower().endswith((".txt", ".md")):
            path = os.path.join(DATA_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    out[fname] = f.read()
            except Exception as e:
                st.warning(f"Could not read {fname}: {e}")
    return out

def search_docs(query: str, pdf_docs: dict, text_docs: dict, max_hits: int = 4):
    """Naive keyword search across PDFs and text files. Returns list of results."""
    q = query.strip()
    if not q:
        return []

    results = []
    # PDFs: return first matches per document (limit total)
    for fname, pages in pdf_docs.items():
        for page_num, text in pages:
            if q.lower() in (text or "").lower():
                results.append({
                    "source": fname,
                    "page": page_num,
                    "snippet": _excerpt(text, q)
                })
                break  # one hit per PDF is enough for this simple demo
        if len(results) >= max_hits:
            break

    # Text/Markdown
    if len(results) < max_hits:
        for fname, text in text_docs.items():
            if q.lower() in (text or "").lower():
                results.append({
                    "source": fname,
                    "page": None,
                    "snippet": _excerpt(text, q)
                })
            if len(results) >= max_hits:
                break

    return results

def create_ticket(name: str, email: str, summary: str, description: str) -> str:
    """Append a support ticket row to /tmp/tickets.csv."""
    row = {
        "name": name.strip(),
        "email": email.strip(),
        "summary": summary.strip(),
        "description": description.strip(),
    }
    if os.path.exists(TICKET_FILE):
        df = pd.read_csv(TICKET_FILE)
    else:
        df = pd.DataFrame(columns=["name", "email", "summary", "description"])
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(TICKET_FILE, index=False)
    return f"Ticket saved to {TICKET_FILE}"

# ---- UI ----
st.set_page_config(page_title="Customer Support Chatbot", page_icon="💬", layout="wide")
st.title("Customer Support Chatbot")

with st.sidebar:
    st.subheader("About")
    st.write("Answers questions from documents in the `/data` folder. "
             "If an answer is not found, you can create a support ticket.")
    st.write("Tickets are stored in a CSV file at `/tmp/tickets.csv`.")
    # Show available files
    st.subheader("Loaded documents")
    try:
        st.write(sorted(os.listdir(DATA_DIR)))
    except FileNotFoundError:
        st.error("`data/` folder not found. Please add your PDFs and .md/.txt files.")

# Load docs (cached)
pdf_docs = load_pdfs()
text_docs = load_texts()

# Conversation history
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_ticket" not in st.session_state:
    st.session_state.pending_ticket = None

# Render history
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

# Chat input
user_q = st.chat_input("Ask a question about the manuals or company info…")
if user_q:
    st.session_state.history.append(("user", user_q))
    with st.chat_message("user"):
        st.markdown(user_q)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents…"):
            hits = search_docs(user_q, pdf_docs, text_docs, max_hits=4)

        if hits:
            lines = ["I found the following references:"]
            for h in hits:
                cite = f"**{h['source']}**"
                if h["page"]:
                    cite += f" p.{h['page']}"
                lines.append(f"- {cite}: {h['snippet']} …")
            answer = "\n".join(lines)
            st.markdown(answer)
            st.session_state.history.append(("assistant", answer))
        else:
            answer = ("I couldn’t find this in the current documents. "
                      "Would you like to create a support ticket?")
            st.markdown(answer)
            st.session_state.history.append(("assistant", answer))
            st.session_state.pending_ticket = user_q

# Ticket form
if st.session_state.pending_ticket:
    st.divider()
    st.subheader("Create Support Ticket")
    with st.form("ticket_form"):
        name = st.text_input("Your name")
        email = st.text_input("Your email")
        summary = st.text_input("Summary (title)", st.session_state.pending_ticket[:80])
        description = st.text_area(
            "Description",
            f"User question:\n{st.session_state.pending_ticket}\n\n"
            "Additional details:"
        )
        submit = st.form_submit_button("Submit ticket")
    if submit:
        msg = create_ticket(name, email, summary, description)
        st.success(msg)
        st.session_state.pending_ticket = None
