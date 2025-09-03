# app.py — Customer Support Chat (RAG + GitHub Tickets)

import os, json, glob
from typing import List, Dict, Tuple

import streamlit as st
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tickets import create_ticket

# ---------------- Company Info ----------------
COMPANY_NAME  = os.getenv("COMPANY_NAME",  "Acme Support")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "support@acme.example")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+1 (555) 010-0101")

# ---------------- Paths & Models ----------------
DATA_DIR   = "data"
VEC_DIR    = "vector_store"
INDEX_PATH = os.path.join(VEC_DIR, "index.faiss")
META_PATH  = os.path.join(VEC_DIR, "meta.json")
CHUNKS_PATH= os.path.join(VEC_DIR, "chunks.jsonl")

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SUMM_MODEL_NAME  = "google/flan-t5-small"

CONF_THRESHOLD   = float(os.getenv("CONF_THRESHOLD", "0.40"))  # stricter
CHUNK_SIZE       = int(os.getenv("CHUNK_SIZE", "600"))

os.makedirs(VEC_DIR, exist_ok=True)

# ---------------- Ingest & Index ----------------
def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _read_pdf_pages(path: str) -> List[str]:
    if fitz is None:
        raise ImportError("PyMuPDF required to read PDFs.")
    doc = fitz.open(path)
    pages = [doc[i].get_text() for i in range(len(doc))]
    doc.close()
    return pages

def _chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= size:
            cur = (cur + "\n" + p).strip()
        else:
            if cur: chunks.append(cur)
            cur = p
    if cur: chunks.append(cur)
    return chunks

def build_corpus() -> List[Dict]:
    corpus = []
    for path in glob.glob(os.path.join(DATA_DIR, "*")):
        fname = os.path.basename(path)
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".txt", ".md"]:
            for ch in _chunk_text(_read_text_file(path)):
                corpus.append({"text": ch, "meta": {"source": fname, "page": 1}})
        elif ext == ".pdf":
            for i, page_text in enumerate(_read_pdf_pages(path), start=1):
                for ch in _chunk_text(page_text):
                    corpus.append({"text": ch, "meta": {"source": fname, "page": i}})
    return corpus

def build_index(corpus: List[Dict]):
    model = SentenceTransformer(EMBED_MODEL_NAME)
    texts = [c["text"] for c in corpus]
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs.astype("float32"))
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump([c["meta"] for c in corpus], f)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for c in corpus:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

def ensure_index_built():
    if not any(os.scandir(DATA_DIR)):
        raise RuntimeError("No documents in data/. Upload at least one .pdf and one .txt/.md.")
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH) and os.path.exists(CHUNKS_PATH)):
        corpus = build_corpus()
        if not corpus:
            raise RuntimeError("Data folder is present but empty of usable content.")
        build_index(corpus)

# ---------------- RAG Engine ----------------
class RAGEngine:
    def __init__(self, top_k: int = 5):
        self.index = faiss.read_index(INDEX_PATH)
        self.embedder = SentenceTransformer(EMBED_MODEL_NAME)
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            self.chunks = [json.loads(x) for x in f]
        self.top_k = top_k

        self.tok = AutoTokenizer.from_pretrained(SUMM_MODEL_NAME)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(SUMM_MODEL_NAME)

    def _embed(self, text: str):
        return self.embedder.encode([text], normalize_embeddings=True, convert_to_numpy=True).astype("float32")

    def _expand_query(self, q: str) -> str:
        synonyms = {
            "maintenance": ["service", "inspection", "upkeep"],
            "connectivity": ["network", "wifi", "connection"],
            "troubleshoot": ["diagnose", "fix", "resolve", "steps"],
            "warranty": ["guarantee", "coverage"],
            "reset": ["factory reset", "restore defaults"],
        }
        extra = []
        lower = q.lower()
        for k, vals in synonyms.items():
            if k in lower:
                extra.extend(vals)
        return q + " " + " ".join(extra)

    def retrieve(self, q: str) -> List[Dict]:
        q_expanded = self._expand_query(q)
        scores, idxs = self.index.search(self._embed(q_expanded), self.top_k)
        out = []
        for sc, idx in zip(scores[0], idxs[0]):
            if idx != -1:
                out.append({"score": float(sc), "meta": self.meta[idx], "text": self.chunks[idx]["text"]})
        return out

    def summarize(self, q: str, context: str) -> str:
        prompt = f"Answer briefly and clearly.\nQuestion: {q}\nContext: {context}\nAnswer:"
        inputs = self.tok(prompt, return_tensors="pt", truncation=True)
        outputs = self.llm.generate(**inputs, max_new_tokens=96)
        return self.tok.decode(outputs[0], skip_special_tokens=True).strip()

    def answer(self, q: str) -> Tuple[str, List[Dict], float]:
        hits = self.retrieve(q)
        if not hits:
            return "", [], 0.0
        context = " ".join(h["text"] for h in hits)
        summary = self.summarize(q, context)
        best = hits[0]["score"] if hits else 0.0
        return summary, hits, best

def format_citations(citations: List[Dict]) -> str:
    if not citations: return ""
    return "\n".join(
        f"Source: **{c['meta']['source']}**, page **{c['meta']['page']}** (score {c['score']:.2f})"
        for c in citations
    )

# ---------------- Streamlit UI ----------------
APP_TITLE = "💬 Customer Support Chat (RAG + GitHub Tickets)"
st.set_page_config(page_title=APP_TITLE, page_icon="💬", layout="wide")

with st.sidebar:
    st.title("ℹ️ Company")
    st.markdown(f"**Name:** {COMPANY_NAME}")
    st.markdown(f"**Email:** {COMPANY_EMAIL}")
    st.markdown(f"**Phone:** {COMPANY_PHONE}")
    st.markdown("---")
    st.subheader("Index & Data")
    if st.button("🔁 Rebuild index"):
        for f in [INDEX_PATH, META_PATH, CHUNKS_PATH]:
            if os.path.exists(f): os.remove(f)
        st.experimental_rerun()
    st.caption("The app auto-builds a FAISS index from files in `data/`.")

with st.spinner("Loading knowledge base..."):
    ensure_index_built()
engine = RAGEngine()

# chat history + ticket form flag
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": f"Hi! I'm your {COMPANY_NAME} support assistant. "
                    f"Ask me about our products. If I can’t find an answer, I’ll help you create a GitHub ticket."}
    ]
if "open_ticket_form" not in st.session_state:
    st.session_state.open_ticket_form = False

st.title(APP_TITLE)
for m in st.session_state.messages:
    st.chat_message(m["role"]).markdown(m["content"])

user_input = st.chat_input("Type your question (or '/ticket' to open the ticket form)")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    if user_input.strip().lower().startswith("/ticket"):
        st.session_state.open_ticket_form = True
    else:
        with st.spinner("Searching knowledge base..."):
            answer, cits, best_score = engine.answer(user_input)

        # relevance check
        keywords = user_input.lower().split()
        relevance = any(k in answer.lower() for k in keywords)

        if (not answer.strip()) or best_score < CONF_THRESHOLD or not relevance:
            msg = ("I couldn't find a confident answer in the docs. "
                   "Would you like to create a support ticket? Open **Create Ticket** below.")
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").markdown(msg)
            st.session_state.open_ticket_form = True
        else:
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").markdown(answer)
            with st.expander("📖 Sources"):
                st.markdown(format_citations(cits))

# ---------------- Ticket Form (shows only if needed) ----------------
if st.session_state.open_ticket_form:
    st.markdown("---")
    st.subheader("📨 Create GitHub Ticket")

    with st.expander("Create Ticket", expanded=True):
        with st.form("ticket_form"):
            user_name  = st.text_input("Your Name",  placeholder="Jane Smith")
            user_email = st.text_input("Your Email", placeholder="jane@example.com")
            title      = st.text_input("Summary / Title", placeholder="Cannot connect to Wi-Fi")
            description= st.text_area("Description / Details", height=160,
                                      placeholder="Steps to reproduce, expected vs actual...")

            submit = st.form_submit_button("Create Ticket")
            if submit:
                if not (user_name and user_email and title and description):
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Creating GitHub issue..."):
                        ok, url_or_msg = create_ticket(
                            title=title,
                            description=description,
                            user_name=user_name,
                            user_email=user_email,
                            user_query=user_input  # pass original query
                        )
                    if ok:
                        st.success(f"✅ Ticket created: {url_or_msg}")
                        st.session_state.open_ticket_form = False
                    else:
                        st.error(f"❌ Failed to create ticket: {url_or_msg}")
