
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

print("Listing models...")
available_models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTesting models for quota...")
found = False
for model_name in available_models:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print("SUCCESS")
        print(f"WORKING MODEL: {model_name}")
        found = True
        break
    except Exception as e:
        print(f"FAILED: {e}")

if not found:
    print("No working model found.")
