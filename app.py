import streamlit as st

st.set_page_config(page_title="Secure Demo")

# ✅ New recommended syntax
query_params = st.query_params
token = query_params.get("key", None)

# ✅ Your valid token
VALID_TOKEN = "abc123"

if token == VALID_TOKEN:
    st.success("✅ Access granted via Power Apps")
    st.title("Welcome to the Secure Streamlit Demo")
    st.write("Only users who came through Power Apps can see this content.")
else:
    st.error("🚫 Access denied")
    st.stop()
