
import google.generativeai as genai
import os
import streamlit as st

# Load key from secrets or env
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No API Key found.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Hello")
    print("SUCCESS: API Key is valid and gemini-2.5-flash is responding.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"ERROR: API Key check failed. {e}")
