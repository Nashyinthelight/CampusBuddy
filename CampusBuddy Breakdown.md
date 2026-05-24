CampusBuddy Breakdown

Tools and Framework- LangChain, ChromaDB, HuggingFace Transformers, Anthropic SDK, Streamlit
_____________________
injest.py

First it goes through \ data/ folders and grabs every .txt and .pdf file.
Then it labels each document with its category (policies/academics/campus_life) and filename, so later answers can cite sources.
Then it splits long documents into character chunks with a set character overlap (Langchain). Set smaller for better precision when searching with some overlap to preserve context when possible.
Convert to vectors (HuggingFace) — Turns each chunk.
Then saves all the chunks + their vectors, not before wiping the ChromaDB folder to make sure its clean before adding the vectors

_____________________
query.py

Uses HuggingFace to convert user question into vectors and uses database to find similar chucks for answer. If no relevent chunks are found the response defaults to an "I don't know" before the Anthropic AI gets called.
Sources are required in the ansdwers, so context is made with the file name/category for citing sources
Chuncks are sent to Anthropic API and uses the question to generate a response

____________________
app.py
Uses streamlab to draw UI for user