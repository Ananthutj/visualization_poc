import streamlit as st
import requests
import os


st.set_page_config(page_title="Secure Streamlit Portal", page_icon="🔐")
st.title("🔐 Secure Streamlit Portal")


flow_url = st.secrets.get("FLOW_VALIDATE_URL") or "https://a3c669f6ac2e4e77ad43beab3e15be.e7.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/97857491b2454e84a8805a65aca4e310/triggers/manual/paths/invoke?api-version=1"

params = st.experimental_get_query_params()
email_param = params.get("email", [""])[0]
token_param = params.get("token", [""])[0]

if not email_param or not token_param:
    st.error("Missing access parameters. Please launch the app via Power Apps.")
    st.stop()

st.write("Please confirm your email to access the portal.")

user_input = st.text_input("Enter your email:", value=email_param)

if st.button("Submit"):
    # Prepare JSON payload
    payload = {
        "email": user_input,
        "token": token_param
    }

    try:
        response = requests.post(flow_url, json=payload)
        response.raise_for_status()  # Raise error if HTTP status is not 200
        result = response.json()

        # Check validation
        if result.get("valid"):
            st.success(f"✅ Access granted! Welcome {user_input}")
            st.write("This is your Streamlit portal content.")
        else:
            st.error("❌ Invalid email or token.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to validation service: {e}")
