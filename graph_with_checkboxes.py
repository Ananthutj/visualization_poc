#This is the code for the graph with checkboxes in the sidebar to show graphs
#1. with products
#2. without products

import streamlit as st
import pandas as pd
import graphviz
import textwrap

st.set_page_config(page_title="Data Flow Graph", layout="wide")
st.title("L-R Directed Data Flow")

file_path = "Sooraj7.xlsx"
sheet1 = "Sheet1"
sheet2 = "Sheet2"

df = pd.read_excel(file_path, sheet_name=sheet1)
df_desc = pd.read_excel(file_path, sheet_name=sheet2)

df.columns = df.columns.str.strip().str.lower()
df.rename(columns={
    "product": "Product",
    "source system": "Source",
    "connection": "Connection",
    "target system": "Target",
    "upstream system": "Upstream",
    "downstream system": "Downstream"
}, inplace=True)

st.sidebar.header("Filters")


upstream_options = ["All"] + sorted(df["Upstream"].dropna().unique().tolist())
upstream_filter = st.sidebar.selectbox("Parent System:", upstream_options)

if upstream_filter != "All":
    df_filtered_upstream = df[df["Upstream"] == upstream_filter]
    product_options = ["All"] + sorted(df_filtered_upstream["Product"].dropna().unique().tolist())
    target_options = ["All"] + sorted(df_filtered_upstream["Target"].dropna().unique().tolist())
else:
    product_options = ["All"] + sorted(df["Product"].dropna().unique().tolist())
    target_options = ["All"] + sorted(df["Target"].dropna().unique().tolist())

product_filter = st.sidebar.selectbox("Product:", product_options)
target_filter = st.sidebar.selectbox("System:", target_options)
show_with_products = st.sidebar.checkbox("Summary Graph", value=True)
show_without_products = st.sidebar.checkbox("Detailed Graph", value=False)

if not show_with_products and not show_without_products:
    st.sidebar.warning("Please select at least one option to display.")

filtered_df = df.copy()
if upstream_filter != "All":
    filtered_df = filtered_df[filtered_df["Upstream"] == upstream_filter]
if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product"] == product_filter]
# if target_filter != "All":
#     filtered_df = filtered_df[filtered_df["Target"] == target_filter]

filtered_df = df.copy()

if upstream_filter != "All":
    filtered_df = filtered_df[filtered_df["Upstream"] == upstream_filter]

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product"] == product_filter]

if target_filter != "All":
    filtered_df = filtered_df[(filtered_df["Source"] == target_filter) | (filtered_df["Target"] == target_filter)
]

unique_edges = filtered_df[["Source", "Connection", "Target"]].drop_duplicates()

products_by_pair = (
    filtered_df.groupby(["Source", "Target"])["Product"]
    .apply(lambda x: sorted(set(x.dropna())))
    .to_dict()
)

sources = set(unique_edges["Source"])
targets = set(unique_edges["Target"])
upstream_nodes = sources - targets
downstream_nodes = targets - sources

def get_color(node):
    if node in upstream_nodes:
        return "#6DB4ED"
    elif node in downstream_nodes:
        return "#4CAF50"
    else:
        return "#FFC107"

def wrap_text(text, width=30):
    """Wrap text with <BR/> for Graphviz HTML-like labels."""
    return "<BR/>".join(textwrap.wrap(text, width=width))

def add_node(dot_obj, node, color, include_products=False):
    """Add node with or without products."""
    incoming = []
    outgoing = []

    for (src, tgt), plist in products_by_pair.items():
        if tgt == node:
            incoming.extend(plist)
        if src == node:
            outgoing.extend(plist)

    incoming = sorted(set(incoming))
    outgoing = sorted(set(outgoing))

    source_row = df_desc[df_desc["Source_Code"].astype(str).str.strip() == str(node).strip()]
    system_name = source_row["Source_System"].iloc[0] if not source_row.empty else ""
    desc = source_row["Source_Desc"].iloc[0] if not source_row.empty else ""

    wrapped_system_name = wrap_text(str(system_name), width=30)

    header_lines = f"""
    <TABLE BORDER="0" CELLBORDER="0" CELLPADDING="1" CELLSPACING="0">
        <TR><TD ALIGN="CENTER"><B><FONT POINT-SIZE='10'>{node}</FONT></B></TD></TR>
        <TR><TD ALIGN="CENTER"><FONT POINT-SIZE='9'>{wrapped_system_name}</FONT></TD></TR>
        <TR><TD ALIGN="CENTER"><FONT POINT-SIZE='9'>{desc}</FONT></TD></TR>
    </TABLE>
    """

    rows = f"""
    <TR><TD ALIGN="CENTER" BORDER="0" CELLPADDING="3" VALIGN="MIDDLE">{header_lines}</TD></TR>
    """

    if include_products:
        rows += """<TR><TD BORDER="0" BGCOLOR="black" HEIGHT="1" FIXEDSIZE="TRUE" WIDTH="100%"></TD></TR>"""
        rows += f"""<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="10"><B><U>Products</U></B></FONT></TD></TR>"""
        all_products = sorted(set(incoming + outgoing))
        if all_products:
            for p in all_products:
                wrapped = wrap_text(str(p), width=30)
                rows += f"""<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{p}</FONT></TD></TR>"""

    label = f"""<
    <TABLE BORDER="1" CELLBORDER="0" CELLPADDING="3" CELLSPACING="0"
           ALIGN="CENTER" BGCOLOR="{color}">
        {rows}
    </TABLE>
    >"""

    dot_obj.node(node, label=label, shape="none", fontsize="16", fontname="Arial")

def build_graph(include_products=False):
    dot = graphviz.Digraph(format="svg")
    dot.attr(rankdir="LR", fontname="Calibri", ratio="fill")
    added_nodes = set()

    for _, row in unique_edges.iterrows():
        s, c, t = row["Source"], row["Connection"], row["Target"]

        if s not in added_nodes:
            add_node(dot, s, get_color(s), include_products=include_products)
            added_nodes.add(s)

        if t not in added_nodes:
            add_node(dot, t, get_color(t), include_products=include_products)
            added_nodes.add(t)

        dot.edge(s, t, label=c)

    return dot

if show_with_products or show_without_products:

    if show_without_products:
        st.subheader("Detailed Graph")
        dot_without = build_graph(include_products=True)
        # st.graphviz_chart(dot_without, use_container_width=True)
        st.graphviz_chart(dot_without, width="stretch")
        

    if show_with_products:
        st.subheader("Summary Graph")
        dot_with = build_graph(include_products=False)
        #st.graphviz_chart(dot_with, use_container_width=True)
        st.graphviz_chart(dot_with, width="stretch")
       

else:
    st.warning("Please select at least one option to display the graph.")


