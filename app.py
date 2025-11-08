import streamlit as st

# ---------------------------
# Streamlit page setup
# ---------------------------
st.set_page_config(page_title="Secure Streamlit Portal", layout="centered")
st.title("🔐 Secure Streamlit Portal")

# ---------------------------
# Get query parameters from URL
# ---------------------------
params = st.experimental_get_query_params()
url_email = params.get("email", [""])[0]
token = params.get("token", [""])[0]  # raw token from URL (hidden from user)

if not url_email or not token:
    st.error("Missing access parameters. Please launch via Power Apps.")
    st.stop()

# ---------------------------
# Input field for user email
# ---------------------------
user_email = st.text_input("Enter your email to access the portal:")

if st.button("Submit"):
    if not user_email:
        st.error("Please enter your email.")
    elif user_email.strip().lower() != url_email.strip().lower():
        st.error("❌ Email does not match the link.")
    else:
        st.success(f"✅ Access granted! Welcome {user_email}")
        
        # ---------------------------
        # Main secure content goes here
        # ---------------------------
        st.write("This is your secure Streamlit portal content.")

        # Optional: you can internally log the token or use it for future server-side validation
        # st.write(f"Token (hidden from user) for internal validation: {token}")
