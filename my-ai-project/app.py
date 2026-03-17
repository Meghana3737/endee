import warnings
warnings.filterwarnings("ignore")

from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Load dataset
with open("dataset.txt", "r") as f:
    documents = f.readlines()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert dataset into embeddings
doc_embeddings = model.encode(documents)

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    best_result = ""
    confidence = 0

    if request.method == "POST":
        query = request.form["query"]
        crop = request.form.get("crop")

        # Combine crop + query
        if crop:
            query = crop + " " + query

        # Image (optional UI feature)
        image = request.files.get("image")

        # Convert query into embedding
        query_embedding = model.encode([query])

        # Compute similarity
        similarity = np.dot(doc_embeddings, query_embedding.T).flatten()

        max_score = np.max(similarity)

        # If no good match
        if max_score < 0.3:
            results = ["⚠️ No relevant disease found."]
            best_result = "Try describing symptoms more clearly."
        else:
            # Get top 3 results
            top_indices = np.argsort(similarity)[::-1][:3]

            results = []

            for i in top_indices:
                text = documents[i]

                # Try structured format (optional)
                parts = text.split("|")

                if len(parts) == 3:
                    disease, symptoms, solution = parts
                    formatted = f"{disease.strip()} - {symptoms.strip()} → {solution.strip()}"
                    results.append(formatted)
                else:
                    results.append(text.strip())

            best_result = results[0]
            confidence = round(max_score * 100, 2)

    return render_template(
        "index.html",
        results=results,
        best_result=best_result,
        confidence=confidence
    )

if __name__ == "__main__":
    app.run(debug=True)