# import streamlit as st
# import base64

# st.title("🔐 Secure Streamlit Portal")

# # Simulated URL parameter: data=YWxpY2VAY29tcGFueS5jb206MTIzNGFiY2QtNTY3OA==
# params = st.experimental_get_query_params()
# data_encoded = params.get("data", [""])[0]

# # Decode
# decoded = base64.b64decode(data_encoded).decode("utf-8")
# url_email, token = decoded.split(":")

# # Ask user to enter email
# user_email = st.text_input("Enter your email:")

# if st.button("Submit"):
#     if user_email.strip().lower() != url_email.strip().lower():
#         st.error("❌ Email does not match.")
#     else:
#         st.success(f"✅ Access granted! Welcome {user_email}")
#         st.write("This is your secure Streamlit portal content.")
#         st.write(f"(Token for internal use: {token})")



import streamlit as st
import base64

st.set_page_config(page_title="Secure Streamlit Portal", layout="centered")
st.title("🔐 Secure Streamlit Portal")

# ---------------------------
# Get the Base64 encoded email from URL
# ---------------------------
params = st.experimental_get_query_params()
encoded_data = params.get("data", [""])[0]

if not encoded_data:
    st.error("❌ Invalid access. Please open this app through Power Apps.")
    st.stop()

# Decode the email
try:
    decoded_email = base64.b64decode(encoded_data).decode("utf-8")
except Exception:
    st.error("❌ Invalid or corrupted link.")
    st.stop()

# ---------------------------
# Ask user to enter their email for verification
# ---------------------------
st.write("Please verify your email to continue:")
user_email = st.text_input("Enter your company email:")

if st.button("Verify"):
    if not user_email:
        st.warning("Please enter your email.")
    elif user_email.strip().lower() == decoded_email.strip().lower():
        st.success(f"✅ Access granted! Welcome, {user_email}")
        
        # ---------------------------
        # Secure section (visible only after verification)
        # ---------------------------
        st.write("This is your secure content area.")
        st.write("You can now show dashboard, data, or reports here.")

    else:
        st.error("❌ Email does not match. Access denied.")
