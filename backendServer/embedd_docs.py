import json
import requests
import boto3
import re
import os
import PyPDF2
import re

#s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')

OPENSEARCH_ENDPOINT = "http://localhost:9200"
INDEX_NAME = "my-vector-index"

mapping = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "text": { "type": "text" },
            "vector": {
                "type": "knn_vector",
                "dimension": 1024
            }
        }
    }
}

response = requests.put(
    f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}",
    headers={"Content-Type": "application/json"},
    data=json.dumps(mapping)
)

def split_text(text, max_chunk_words=50):
    sentences = re.split(r'(?<=[-.!?])\s+', text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        words = sentence.split()
        if sum(len(s.split()) for s in current_chunk) + len(words) <= max_chunk_words:
            current_chunk.append(sentence)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def get_pdf_text(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def get_embedding(text):
    body = {
        "inputText": text[:8000]
    }
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(body),
        contentType="application/json"
    )
    return json.loads(response['body'].read())['embedding']

def store_in_opensearch(text, vector):
    document = {
        "text": text,
        "vector": vector
    }
    response = requests.post(
        f"{OPENSEARCH_ENDPOINT}/{INDEX_NAME}/_doc/",
        headers={"Content-Type": "application/json"},
        json=document
    )
    # print(f"OpenSearch response: {response.status_code} — {response.text}")
    return response.status_code

def embedd_from_path(path):
    text = get_pdf_text(path)
    status = []

    for chunk in split_text(text):
        print(chunk, "\n\n")
        vector = get_embedding(chunk)
        status.append(store_in_opensearch(chunk, vector))


    # print(status)
    # print(json.dumps('success'))

def embedd_from_text(text):
    status = []

    for chunk in split_text(text):
        vector = get_embedding(chunk)
        status.append(store_in_opensearch(chunk, vector))

    # print(status)
    # print(json.dumps('success'))


if __name__ == "__main__":
    paths = ["./Remote_work_policy.pdf"]
    for path in paths:
       embedd_from_path(path)
    print("documents embedded.")