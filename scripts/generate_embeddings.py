import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Load your dataset
df = pd.read_excel("ua_resources_filled.xlsx")

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# Use search_text column
texts = df["search_text"].tolist()

print("Generating embeddings...")

embeddings = model.encode(texts, show_progress_bar=True)

# Save
np.save("embeddings.npy", embeddings)

print("Saved embeddings.npy ✅")
