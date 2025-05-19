"""
IBM Granite Model Integration for SmartLearn Platform

This module provides functions to interact with the IBM Granite LLM.
"""

import requests
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MODEL_ID = "ibm-granite/granite-3.3-2b-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    st.error("⚠️ Hugging Face API token not found. Please set HF_TOKEN in your .env file.")
    st.info("You can get your token from: https://huggingface.co/settings/tokens")
    headers = None
else:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def initialize_granite_model():
    if not HF_TOKEN:
        return None
    return {"api_url": API_URL, "headers": headers, "model_name": MODEL_ID}

def generate_granite_response(granite_model, prompt, max_tokens=512):
    if not granite_model or not granite_model.get("headers"):
        return "Error: Hugging Face API token not configured. Please set HF_TOKEN in your .env file."
        
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens},
        "options": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(
            granite_model["api_url"],
            headers=granite_model["headers"],
            json=payload,
            timeout=30  # Add timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return result[0]["generated_text"]
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            elif isinstance(result, list) and len(result) > 0 and "generated_text" in result[0].get('generated_text', {}):
                return result[0]['generated_text']
            else:
                return str(result)
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            st.error(error_msg)
            return error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to Hugging Face API: {str(e)}"
        st.error(error_msg)
        return error_msg