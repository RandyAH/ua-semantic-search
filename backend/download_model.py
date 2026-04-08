from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
model.save("/app/model")
print("Model downloaded and saved to /app/model")