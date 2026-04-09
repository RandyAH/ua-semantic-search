# UA Semantic Search System

A cloud-deployed semantic search engine that enables fast, relevant retrieval of structured university resources using vector embeddings.

This project demonstrates how to design and deploy a **data-driven backend system** that transforms raw data into an efficient, queryable search experience.

---

## 🚀 Overview

The UA Semantic Search System allows users to search across university resources using natural language queries.

Instead of keyword matching, the system uses **embedding-based similarity** to return contextually relevant results.

---

## 🧠 Key Features

- Semantic search using transformer-based embeddings  
- FastAPI backend for real-time query processing  
- Precomputed embeddings for low-latency retrieval  
- Vector similarity ranking (cosine / dot product)  
- Cloud deployment with Docker  
- End-to-end data pipeline from raw dataset to searchable system  

---

## 🏗️ System Architecture

The system follows a simple but scalable pipeline:

1. **Data Ingestion**  
   - Structured dataset of university resources (CSV/Excel)

2. **Data Enrichment**  
   - Generated descriptions, keywords, and metadata

3. **Embedding Generation**  
   - SentenceTransformers model converts text → vector embeddings

4. **Storage**  
   - Embeddings stored as NumPy arrays for fast access

5. **Query Processing**  
   - User query → embedding → similarity search

6. **Ranking & Response**  
   - Top-k results returned via API

---

## ⚡ Performance Optimization

- Reduced query latency from ~5 seconds to <1 second  
- Achieved via:
  - Precomputed embeddings  
  - Vectorized similarity computation  
  - Lazy model loading  

---

## 🛠️ Tech Stack

**Backend:** FastAPI, Python  
**ML / Data:** SentenceTransformers, NumPy, Pandas  
**Deployment:** Docker, Google Cloud Run  
**Frontend:** Next.js  

---

## 📦 API Example

**POST /search**

Request:
```json
{
  "query": "student health services"
}
