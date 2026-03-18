from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load dataset
data = []
texts = []

with open("dataset.txt", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("|")
        if len(parts) == 3:
            disease = parts[0].strip()
            symptoms = parts[1].strip()
            solution = parts[2].strip()

            data.append({
                "disease": disease,
                "symptoms": symptoms,
                "solution": solution
            })

            texts.append(disease + " " + symptoms)

# Convert dataset to embeddings
embeddings = model.encode(texts)

# Store history
history = []
total_searches = 0


@app.route("/", methods=["GET", "POST"])
def home():
    global total_searches

    best_result = None
    results = []
    confidence = 0

    if request.method == "POST":
        query = request.form["query"]

        history.append(query)
        total_searches += 1

        query_embedding = model.encode(query)

        scores = util.cos_sim(query_embedding, embeddings)[0]

        # Get top 3 matches
        top_indices = scores.argsort(descending=True)[:3]

        results = []
        for idx in top_indices:
            results.append(data[int(idx)])

        best_result = results[0]
        confidence = round(float(scores[top_indices[0]]) * 100, 2)

    return render_template(
        "index.html",
        best_result=best_result,
        results=results,
        confidence=confidence,
        history=history,
        total=total_searches
    )


if __name__ == "__main__":
    app.run(debug=True)