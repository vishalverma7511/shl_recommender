from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
import os

# Globals for lazy loading
model = None
catalog = None
catalog_embeddings = None

def load_resources():
    global model, catalog, catalog_embeddings
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')

    if catalog is None or catalog_embeddings is None:
        DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "shl_catalog.json")
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)
        catalog_texts = [item["Assessment Name"] for item in catalog_data]
        catalog_embeds = model.encode(catalog_texts, convert_to_tensor=True)

        catalog = catalog_data
        catalog_embeddings = catalog_embeds

def clean_unicode_symbols(data):
    return data.replace("\u2718", "✘").replace("\u2714", "✓")

def recommend_assessments(query, top_k=5):
    load_resources()  # Ensure everything is loaded only when needed

    query_embedding = model.encode([query], convert_to_tensor=True)
    similarities = cosine_similarity(query_embedding, catalog_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for i in top_indices:
        item = catalog[i]
        result = {
            "Assessment Name": item["Assessment Name"],
            "Remote Testing": item["Remote Testing"],
            "Adaptive/IRT": item["Adaptive/IRT"],
            "Test Type": item["Test Type"],
            "URL": item["URL"],
            "Duration": item["Duration"],
        }
        results.append(result)

    return results

def demo():
    query = "We are hiring for a sales leadership role with strong analytical ability"
    top_results = recommend_assessments(query, top_k=5)

    print("\nTop Recommendations:\n")
    for i, item in enumerate(top_results, 1):
        print(f"{i}. {item['Assessment Name']}")
        print(f"   URL: {item['URL']}")
        print(f"   Remote Testing: {item['Remote Testing']}")
        print(f"   Adaptive/IRT: {item['Adaptive/IRT']}")
        print(f"   Test Type: {item['Test Type']}")
        print(f"   Duration: {item['Duration']}\n")

if __name__ == "__main__":
    demo()
