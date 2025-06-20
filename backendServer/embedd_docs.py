import json
import requests
import boto3
import re
import os
import PyPDF2

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

def split_text(text, chunk_size=100):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

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
    print(f"OpenSearch response: {response.status_code} — {response.text}")
    return response.status_code

def embedd_from_path(path):
    text = get_pdf_text(path)
    status = []

    for chunk in split_text(text):
        vector = get_embedding(chunk)
        status.append(store_in_opensearch(chunk, vector))


    print(status)
    print(json.dumps('success'))

def embedd_from_text(text):
    status = []

    for chunk in split_text(text):
        vector = get_embedding(chunk)
        status.append(store_in_opensearch(chunk, vector))

    print(status)
    print(json.dumps('success'))


if __name__ == "__main__":
   paths = ["./MOCK_HR_DOC.pdf"]
   for path in paths:
       embedd_from_path(path)