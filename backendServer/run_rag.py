import boto3
import requests
import json

#Config
OPENSEARCH_ENDPOINT = "http://localhost:9200"
OPENSEARCH_INDEX = "my-vector-index"
VECTOR_FIELD = "vector"
K = 1  # Top-K retrieved chunks
BEDROCK_REGION = "us-east-2"
GEMINI_API_KEY = "AIzaSyBnllNus3WXLaZ8ki7kWKaA2ZCgDunhgzQ"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

#Clients
bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

#Embedding
def get_titan_embedding(text):
    body = {"inputText": text[:8000]}
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(body),
        contentType="application/json"
    )
    return json.loads(response['body'].read())['embedding']

# Vector Search
def knn_search(query_vector):
    url = f"{OPENSEARCH_ENDPOINT}/{OPENSEARCH_INDEX}/_search"
    body = {
        "size": K,
        "query": {
            "knn": {
                VECTOR_FIELD: {
                    "vector": query_vector,
                    "k": K
                }
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(body))
    response.raise_for_status()
    return [hit["_source"]["text"] for hit in response.json()["hits"]["hits"]]

# Build Prompt
def build_prompt(user_question, context_chunks):
    context = "\n\n".join(context_chunks)
    print("Using context:", context)
    return f"""You are a helpful HR assistant designed to answer questions related to various company policies.
    Please use only the context provided to answer the users question. Always be highly professional. Always return answers in a clear and consise manner.
    If the information is not in the context tell the user you do not have that information.

Context:
{context}

Question: {user_question}

Answer:"""

# Generate Response
def call_gemini(prompt):
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_ENDPOINT, headers=headers, data=json.dumps(body))
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# RAG
def run_rag(query_text):
    embedding = get_titan_embedding(query_text)
    chunks = knn_search(embedding)
    print(chunks)
    prompt = build_prompt(query_text, chunks)
    answer = call_gemini(prompt)
    return(answer)

# Main
if __name__ == "__main__":
    user_input = input("Enter your question: ")
    run_rag(user_input)
