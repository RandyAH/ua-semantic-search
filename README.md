# 🔍 UA Semantic Search

A semantic search engine for University of Alabama resources that understands **user intent**, not just keywords.

## 🚀 Overview

Traditional search systems rely on exact keyword matching, which often fails when users don’t know the correct terminology.

This project builds a **semantic search system** that allows users to search naturally (e.g., *“I need help mentally”*) and still retrieve the most relevant university resources (e.g., Counseling Center).

The system uses **machine learning and natural language processing** to map both user queries and resources into vector space and return results based on meaning similarity.

---

## 🧠 Features

* 🔎 Semantic search using sentence embeddings (MiniLM)
* ⚡ FastAPI backend for real-time query handling
* 🌐 Next.js frontend with clean UI
* 📊 TF-IDF baseline model for comparison
* 🧪 Evaluation using precision@k, recall@k, and MRR
* 🧱 Feature engineering with weighted search fields
* 🤖 AI-generated dataset enrichment (descriptions, queries, keywords)

---

## 🏗️ Architecture

```
User Query
   ↓
Embedding Model (MiniLM)
   ↓
Vector Similarity (Cosine)
   ↓
Ranked Results
```

---

## 📊 Models

### 1. TF-IDF (Baseline)

* Keyword-based matching
* Fast and interpretable
* Limited understanding of meaning

### 2. SentenceTransformer (MiniLM)

* Semantic embeddings
* Captures intent and context
* Higher recall and better real-world performance

---

## 📈 Evaluation Metrics

* **Precision@5** – How many of the top results are relevant
* **Recall@5** – Whether all relevant results are retrieved
* **MRR (Mean Reciprocal Rank)** – How early the correct result appears

---

## 📂 Project Structure

```
backend/
  app.py
  semantic_search.py
  embeddings.npy
  ua_resources_filled.xlsx

frontend/
  app/page.tsx

scripts/
  generate_embeddings.py
  fill_dataset.py
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo

```
git clone https://github.com/your-username/ua-semantic-search.git
cd ua-semantic-search
```

---

### 2. Backend setup

```
cd backend
pip install -r requirements.txt
python download_model.py
```

Run server:

```
uvicorn app:app --host 0.0.0.0 --port 8080
```

---

### 3. Frontend setup

```
cd frontend
npm install
npm run dev
```

---

## 🔎 Usage

1. Open the frontend in your browser
2. Enter a natural language query

   * Example: *“how do I plan my classes”*
3. View ranked results based on semantic similarity

---

## 🌐 Deployment

* Backend: Google Cloud Run
* Frontend: Vercel

---

## 🔥 Example Queries

* “I need help mentally” → Counseling resources
* “build my schedule” → Schedule Builder
* “find a job” → Job board

---

## ⚠️ Limitations

* Relies on AI-generated dataset fields
* Small dataset limits generalization
* Embedding model adds latency compared to keyword search

---

## 🚀 Future Improvements

* Add vector database (FAISS, Pinecone, etc.)
* Improve ranking with hybrid search (TF-IDF + embeddings)
* Add user personalization
* Expand dataset coverage

---

## 👨‍💻 Author

Randy Hannah
Computer Science Student – University of Alabama

---

## 📄 License

This project is for educational and research purposes.
