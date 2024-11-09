# from .mashuputil import RAGPipeline
from config import settings
from fastapi import HTTPException
import google.generativeai as genai
import requests
import PyPDF2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# rag_pipeline = RAGPipeline()
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

def prompt_maker(query , context):
    base_prompt = """Answer the query based on the context. Context:- {context}, \n Query:- {query}"""
    base_prompt = base_prompt.format(context = context , query=query)
    return base_prompt

def respond(query, pdf_file: str):
    extracted_text = extract_text_from_pdf(pdf_path=pdf_file)
    prompt = prompt_maker(query, extracted_text)
    response = model.generate_content(prompt)
    return response.text

# def respond(query, pdf_file: str):
#     rag_pipeline = RAGPipeline(model_name_or_path="all-mpnet-base-v2", device="cpu", num_sentence_chunk_size=10)
#     embedded_chunks = rag_pipeline.process_pdf(pdf_path=pdf_file)
#     rag_pipeline.save_embeddings_to_faiss_with_metadata(embedded_chunks, "faiss_index.index", "metadata.json")
#     rag_pipeline.load_faiss_and_metadata("faiss_index.index", "metadata.json")
#     results = rag_pipeline.search_in_faiss(query=query, k=5)
    
#     prompt = prompt_maker(query = query , context=results)
    
#     response = model.generate_content(prompt)
#     return response


  
def summarize(pdf_file:str):
    extracted_text = extract_text_from_pdf(pdf_path=pdf_file)
    prompt = "Summarize the text given text"
    response = model.generate_content([prompt, extracted_text])
    return response.text
    
  
  
# def summarize(pdf_file: str):
#     headers = {
#         'apy-token': settings.apyhub_api_key,  # Ensure this API key is correct
#     }

#     try:
#         # Open the file safely using 'with'
#         with open(pdf_file, 'rb') as file:
#             files = {
#                 'file': file,
#             }

#             # Make the API request
#             logger.info("Sending request to APYHub API...")
#             response = requests.post(
#                 'https://api.apyhub.com/ai/summarize-documents/file',
#                 headers=headers,
#                 files=files
#             )

#         # Check if the response is not 200
#         if response.status_code != 200:
#             logger.error(f"Error from APYHub API: {response.status_code} - {response.text}")
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"Error from APYHub API: {response.text}"
#             )

#         # If successful, return the JSON response
#         return response.json()

#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=404,
#             detail=f"File '{pdf_file}' not found."
#         )

#     except requests.RequestException as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error occurred during API request: {str(e)}"
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )

