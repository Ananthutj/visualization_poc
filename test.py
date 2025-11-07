# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle, FancyArrow
# from PIL import Image
# import os

# # Set up folders and file paths
# input_excel = "Sooraj_poc_sample.xlsx"
# output_folder = "output_images"
# os.makedirs(output_folder, exist_ok=True)

# # Title of the app
# st.title("Generated Relationship Diagrams")

# # Generate images only once
# if "images_generated" not in st.session_state:
#     try:
#         df = pd.read_excel(input_excel)
#         required_cols = ["Product", "Context", "Source", "Relation", "Target"]
#         if not all(col in df.columns for col in required_cols):
#             st.error(f"Excel must have columns: {required_cols}")
#         else:
#             for (product, context), group in df.groupby(["Product", "Context"]):
#                 for idx, row in group.iterrows():
#                     source = row["Source"]
#                     relation = row["Relation"]
#                     target = row["Target"]

#                     fig, ax = plt.subplots(figsize=(6, 3))
#                     ax.set_xlim(0, 10)
#                     ax.set_ylim(0, 5)
#                     ax.axis("off")

#                     ax.text(5, 4.5, f"Product: {product} | Context: {context}",
#                             ha="center", va="center", fontsize=12, fontweight="bold")

#                     src_x, src_y, box_w, box_h = 1, 2, 2, 1
#                     ax.add_patch(Rectangle((src_x, src_y), box_w, box_h,
#                                            facecolor="#0a5d7a", edgecolor="black"))
#                     ax.text(src_x + box_w / 2, src_y + box_h / 2, source,
#                             ha="center", va="center", color="white", fontsize=10)

#                     tgt_x = 6
#                     ax.add_patch(Rectangle((tgt_x, src_y), box_w, box_h,
#                                            facecolor="#0a5d7a", edgecolor="black"))
#                     ax.text(tgt_x + box_w / 2, src_y + box_h / 2, target,
#                             ha="center", va="center", color="white", fontsize=10)

#                     arrow_x = src_x + box_w
#                     arrow_y = src_y + box_h / 2
#                     ax.add_patch(FancyArrow(arrow_x, arrow_y, tgt_x - arrow_x, 0,
#                                             width=0.05, head_width=0.3, head_length=0.3, color="black"))

#                     ax.text((arrow_x + tgt_x) / 2, arrow_y + 0.3, relation,
#                             ha="center", va="center", fontsize=10)

#                     out_name = f"{output_folder}/{product}_{context}_{idx}.png"
#                     plt.savefig(out_name, bbox_inches="tight")
#                     plt.close(fig)

#             st.session_state.images_generated = True
#             st.success("Images generated successfully.")
#     except Exception as e:
#         st.error(f"Error generating images: {e}")

# # Display images
# if os.path.exists(output_folder):
#     image_files = sorted([f for f in os.listdir(output_folder) if f.endswith(".png")])
#     products = sorted(set(f.split("_")[0] for f in image_files if "_" in f))
#     contexts = sorted(set(f.split("_")[1] for f in image_files if "_" in f))

#     selected_product = st.selectbox("Select Product (leave empty to show all)", [""] + products)
#     selected_context = st.selectbox("Select Context (leave empty to show all)", [""] + contexts)

#     for image_file in image_files:
#         parts = image_file.split("_")
#         if len(parts) >= 3:
#             product_match = (selected_product == "" or parts[0] == selected_product)
#             context_match = (selected_context == "" or parts[1] == selected_context)
#             if product_match and context_match:
#                 image_path = os.path.join(output_folder, image_file)
#                 image = Image.open(image_path)
#                 st.image(image, caption=image_file, use_container_width=True)
# else:
#     st.error(f"Folder '{output_folder}' not found.")


import os, matplotlib.pyplot as plt, pandas as pd

# Get OneDrive path
onedrive_path = os.environ.get("OneDrive")
if not onedrive_path:
    raise Exception("OneDrive folder not found. Make sure OneDrive is running.")

# Create folder
folder = os.path.join(onedrive_path, "Documents", "PowerAppsVisuals")
os.makedirs(folder, exist_ok=True)

# Save chart
output_path = os.path.join(folder, "sales_chart.png")
data = {'Month': ['Jan','Feb','Mar'], 'Sales': [150,200,180]}
df = pd.DataFrame(data)
df.plot(kind='bar', x='Month', y='Sales', color='skyblue')
plt.savefig(output_path)
plt.close()

print(f"Chart saved at {output_path}")