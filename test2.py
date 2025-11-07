import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os

# File paths
input_excel = "Sooraj4.xlsx"
output_folder = "output_images1"
os.makedirs(output_folder, exist_ok=True)

st.title("Product & Context Based Relationship Network Graph")

# Load Excel
try:
    df = pd.read_excel(input_excel, engine="openpyxl")
except Exception as e:
    st.error(f"Error reading Excel: {e}")
    st.stop()

required_cols = ["Product", "Context", "Source", "Relation", "Target"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Excel must have columns: {required_cols}")
    st.stop()

# Sidebar filters
product_options = ["All"] + sorted(df["Product"].dropna().unique().tolist())
context_options = ["All"] + sorted(df["Context"].dropna().unique().tolist())

selected_product = st.sidebar.selectbox("Select Product", product_options)
selected_context = st.sidebar.selectbox("Select Context", context_options)

# Apply filtering logic
filtered_df = df.copy()
if selected_product != "All" and selected_context != "All":
    filtered_df = df[(df["Product"] == selected_product) & (df["Context"] == selected_context)]
elif selected_product != "All":
    filtered_df = df[df["Product"] == selected_product]
elif selected_context != "All":
    filtered_df = df[df["Context"] == selected_context]

if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# Build directed graph
G = nx.DiGraph()
for _, row in filtered_df.iterrows():
    G.add_edge(row["Source"], row["Target"], relation=row["Relation"], context=row["Context"])

# Dynamic spacing
num_nodes = len(G.nodes)
base_k = 1.5
spacing_factor = base_k + (num_nodes * 0.25)
pos = nx.spring_layout(G, seed=42, k=spacing_factor, iterations=100)

# Context color mapping (editable)
context_color_map = {
    "Risk": "red",
    "Mitigated": "green",
    "Applied": "blue"
}
default_edge_color = "black"

# Create figure
fig, ax = plt.subplots(figsize=(13, 10))
ax.axis("off")

# Draw edges with arrows
for u, v, data in G.edges(data=True):
    ctx = data.get("context", "")
    edge_color = context_color_map.get(ctx, default_edge_color)
    nx.draw_networkx_edges(
        G, pos, edgelist=[(u, v)], ax=ax,
        arrows=True,
        arrowsize=65,
        width=3.2,
        edge_color=edge_color,
        min_source_margin=30,
        min_target_margin=30,
        connectionstyle="arc3,rad=0.1",
        alpha=0.9
    )

# Draw nodes with slightly larger rectangles and text
for node, (x, y) in pos.items():
    ax.text(
        x, y, node,
        ha="center", va="center",
        bbox=dict(
            boxstyle="round,pad=0.66",   # increased by 10%
            facecolor="#0a5d7a",
            edgecolor="black",
            linewidth=1.8
        ),
        color="white",
        fontsize=18,  # increased by 10%
        fontweight="bold"
    )

# Draw edge labels with color based on context
edge_labels = nx.get_edge_attributes(G, 'relation')
for (u, v), label in edge_labels.items():
    ctx = G[u][v].get("context", "")
    edge_color = context_color_map.get(ctx, default_edge_color)
    ax.text(
        (pos[u][0]+pos[v][0])/2,
        (pos[u][1]+pos[v][1])/2,
        label,
        color=edge_color,
        fontsize=16,
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.6)
    )

# Save and display
filter_name = f"{selected_product}_{selected_context}".replace("All", "AllData")
out_name = os.path.join(output_folder, f"{filter_name}_network.png")

plt.tight_layout()
plt.savefig(out_name, bbox_inches="tight", dpi=200)
plt.close(fig)

st.image(out_name, caption=f"Network Graph ({selected_product} | {selected_context})", use_container_width=True)
st.success(f"Graph generated for Product: {selected_product}, Context: {selected_context}")