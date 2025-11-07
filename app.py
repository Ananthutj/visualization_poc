import streamlit as st
import urllib.parse
 
st.set_page_config(page_title="Secure Demo")
 
# --- Read the secret token from URL ---
query_params = st.query_params
token = query_params.get("key", [None])[0]
 
# --- Define your valid token(s) ---
VALID_TOKEN = "abc123"   # change this to any random string
 
# --- Simple check ---
if token == VALID_TOKEN:
    st.success("✅ Access granted via Power Apps")
    st.title("Welcome to the Secure Streamlit Demo")
    st.write("Only users who came through Power Apps can see this content.")
else:
    st.error("🚫 Access denied")
    st.stop()