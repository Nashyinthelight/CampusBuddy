from google import genai

# 🔑 put your API key here
client = genai.Client(api_key="AIzaSyBpQMVT1M7dB6B96y7VgaN4nMAcsUCt7bs")

with open("data.txt", "r") as f:
    context = f.read()

def ask_question(question):
    prompt = f"""
You are a helpful FAU campus assistant.

Only use the context below. If you don't know, say so.

Context:
{context}

Question:
{question}

Answer clearly:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


while True:
    q = input("Ask a question: ")
    print(ask_question(q))
