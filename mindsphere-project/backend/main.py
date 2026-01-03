from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

app = FastAPI(title="MindSphere - Document Intelligence MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI model (Natural Language Inference)
classifier = pipeline("text-classification", model="roberta-large-mnli")

def split_clauses(text):
    sentences = text.replace("\n", " ").split(".")
    return [s.strip() for s in sentences if len(s.strip()) > 20]

@app.post("/analyze")
async def analyze(file: UploadFile):
    text = (await file.read()).decode("utf-8")
    clauses = split_clauses(text)

    contradictions = []

    for i in range(len(clauses)):
        for j in range(i + 1, len(clauses)):
            pair = clauses[i] + " </s></s> " + clauses[j]
            result = classifier(pair)[0]

            if result["label"] == "CONTRADICTION":
                contradictions.append({
                    "clause_1": clauses[i],
                    "clause_2": clauses[j],
                    "confidence": round(result["score"], 2),
                    "explanation": "These clauses impose conflicting rules or obligations."
                })

    return {
        "total_clauses": len(clauses),
        "contradictions_found": len(contradictions),
        "results": contradictions
    }