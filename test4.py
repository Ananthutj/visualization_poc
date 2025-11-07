import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

# File paths
input_excel = "Sooraj4.xlsx"
output_folder = "output_html"
os.makedirs(output_folder, exist_ok=True)

st.title("Resultant Product & Context Relationship Network Graph")

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

# Apply filters
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

# Context color mapping
context_color_map = {
    "Risk": "red",
    "Treasury": "green",
    "Finance": "blue"
}
default_edge_color = "black"

# Build directed graph
G = nx.DiGraph()
for _, row in filtered_df.iterrows():
    G.add_edge(row["Source"], row["Target"], relation=row["Relation"], context=row["Context"])

# Create PyVis interactive network
net = Network(height="750px", width="100%", bgcolor="#FFFFFF", directed=True, notebook=False)
net.toggle_physics(True)

# --- 💡 Adjust physics settings to increase spacing between nodes ---
net.set_options("""
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -3000,
      "centralGravity": 0.2,
      "springLength": 250,
      "springConstant": 0.02
    },
    "minVelocity": 0.75
  },
  "edges": {
    "font": {
      "multi": "html"
    },
    "smooth": {
      "type": "dynamic"
    },
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 1.2
      }
    },
    "length": 250
  }
}
""")

# Compute in-degree and out-degree
outdegree_count = dict(G.out_degree())
indegree_count = dict(G.in_degree())

# Add nodes with tooltips showing both incoming and outgoing relationships
for node in G.nodes():
    out_count = outdegree_count.get(node, 0)
    in_count = indegree_count.get(node, 0)
    tooltip_text = (
        f"{node} 🔸Incoming Relationships:{in_count}  🔹Outgoing Relationships:{out_count} "
    )
    net.add_node(
        node,
        label=node,
        title=tooltip_text,
        color="#0a5d7a",
        font={"color": "white", "size": 28},
        shape="box",
        borderWidth=4,
        shadow=True,
        size=250
    )

# Add edges with context-based color and bold labels (HTML)
for u, v, data in G.edges(data=True):
    ctx = data.get("context", "")
    edge_color = context_color_map.get(ctx, default_edge_color)
    # wrap relation in <b> so it becomes bold when font.multi is enabled
    relation_html = f"<b>{data.get('relation', '')}</b>"
    net.add_edge(
        u,
        v,
        label=relation_html,
        color=edge_color,
        arrows="to",
        arrowStrikethrough=False,
        width=4,
        length=300,
        font={"multi": "html"}  # ensure this edge allows HTML-style markup
    )

# Save interactive HTML
filter_name = f"{selected_product}_{selected_context}".replace("All", "AllData")
html_path = os.path.join(output_folder, f"{filter_name}_network.html")
net.save_graph(html_path)

# --- 🟦 Add Color Legend Section ---
st.markdown(
    """
    <div style="background-color:#f2f2f2; padding:10px; border-radius:10px; margin-bottom:10px; font-size:16px;">
        <b>🗺️ Color Legend:</b><br>
        <span style="color:red; font-weight:bold;">⬤</span> Risk <br>
        <span style="color:green; font-weight:bold;">⬤</span> Treasury <br>
        <span style="color:blue; font-weight:bold;">⬤</span> Finance 
    </div>
    """,
    unsafe_allow_html=True
)

# Render the graph in Streamlit
st.components.v1.html(open(html_path, "r", encoding="utf-8").read(), height=800, scrolling=True)

st.success(f"Resultant Network generated for Product: {selected_product}, Context: {selected_context}")