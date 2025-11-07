import streamlit as st
import pandas as pd
import graphviz

st.title("Resultant Product & Context Relationship Graph (Graphviz with Hover Tooltips)")

# ---------------------------
# 1️⃣ Load Excel
# ---------------------------
input_excel = "Sooraj5.xlsx"
df = pd.read_excel(input_excel, engine="openpyxl")

required_cols = ["Product", "Context", "Source", "Relation", "Target"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Excel must have columns: {required_cols}")
    st.stop()

# ---------------------------
# 2️⃣ Sidebar filters
# ---------------------------
product_options = ["All"] + sorted(df["Product"].dropna().unique().tolist())
context_options = ["All"] + sorted(df["Context"].dropna().unique().tolist())

selected_product = st.sidebar.selectbox("Select Product", product_options)
selected_context = st.sidebar.selectbox("Select Context", context_options)
layout_dir = st.sidebar.radio("Graph Layout Direction", ["Left → Right", "Top → Bottom"])

# ---------------------------
# 3️⃣ Filter Data
# ---------------------------
filtered_df = df.copy()
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["Product"] == selected_product]
if selected_context != "All":
    filtered_df = filtered_df[filtered_df["Context"] == selected_context]

if filtered_df.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# ---------------------------
# 4️⃣ Group duplicate edges
# ---------------------------
grouped = (
    filtered_df.groupby(["Source", "Target", "Context"])
    .agg({"Relation": lambda x: ", ".join(sorted(set(x)))})
    .reset_index()
)

# ---------------------------
# 5️⃣ Graphviz settings
# ---------------------------
graph_attr = {
    "rankdir": "LR" if layout_dir == "Left → Right" else "TB",
    "bgcolor": "white",
    "splines": "spline",
    "overlap": "false",
    "fontsize": "12",
}

dot = graphviz.Digraph(comment="System Relationship Graph", graph_attr=graph_attr)
dot.attr("node", shape="box", style="filled,rounded", fontname="Helvetica", fontsize="12")

# Context colors
context_color_map = {
    "Risk": "lightcoral",
    "Treasury": "lightgreen",
    "Finance": "lightblue",
}
default_color = "#B0C4DE"

# ---------------------------
# 6️⃣ Add nodes + edges with tooltips
# ---------------------------
all_nodes = set(grouped["Source"]).union(set(grouped["Target"]))
for node in all_nodes:
    node_context = (
        grouped.loc[grouped["Source"] == node, "Context"].head(1).values[0]
        if node in grouped["Source"].values
        else grouped.loc[grouped["Target"] == node, "Context"].head(1).values[0]
    )
    ctx_color = context_color_map.get(node_context, default_color)
    dot.node(
        node,
        tooltip=f"Source Node: {node}",  # <-- Tooltip text
        fillcolor=ctx_color
    )

for _, row in grouped.iterrows():
    dot.edge(
        row["Source"],
        row["Target"],
        label=row["Relation"],
        fontsize="10",
        color="gray40",
        fontcolor="black"
    )

# ---------------------------
# 7️⃣ Render as interactive HTML (SVG)
# ---------------------------
svg_html = dot.pipe(format="svg").decode("utf-8")
st.components.v1.html(svg_html, height=700, scrolling=True)

st.success(f"✅ Interactive Graph with tooltips generated for Product: {selected_product}, Context: {selected_context}")
