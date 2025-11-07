import streamlit as st
from PIL import Image
import os

# Set the title
st.title("Generated Relationship Diagrams")

# Folder containing images
output_folder = "output_images"

# Check if folder exists
if not os.path.exists(output_folder):
    st.error(f"Folder '{output_folder}' not found. Please generate images first.")
else:
    # List all PNG files
    image_files = sorted([f for f in os.listdir(output_folder) if f.endswith(".png")])

    # Extract unique products and contexts from filenames
    products = sorted(set(f.split("_")[0] for f in image_files if "_" in f))
    contexts = sorted(set(f.split("_")[1] for f in image_files if "_" in f))

    # Add dropdown filters with empty options
    selected_product = st.selectbox("Select Product (leave empty to show all)", [""] + products)
    selected_context = st.selectbox("Select Context (leave empty to show all)", [""] + contexts)

    # Display images based on selected filters
    for image_file in image_files:
        parts = image_file.split("_")
        if len(parts) >= 3:
            product_match = (selected_product == "" or parts[0] == selected_product)
            context_match = (selected_context == "" or parts[1] == selected_context)
            if product_match and context_match:
                image_path = os.path.join(output_folder, image_file)
                image = Image.open(image_path)
                st.image(image, caption=image_file, use_container_width=True)