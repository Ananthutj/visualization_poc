#This is the code for the graph with incomging and outgoing products combined in a single node

import streamlit as st
import pandas as pd
import graphviz
import textwrap

st.set_page_config(page_title="FSDF Flow Graph", layout="wide")
st.title("L-R Directed Data Flow")

file_path = "Sooraj7.xlsx"

sheet1 = "Sheet1"
df = pd.read_excel(file_path, sheet_name=sheet1)

sheet2 = "Sheet2"
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

desc_map = dict(zip(df_desc["Source_Code"].astype(str).str.strip(),
                    df_desc["Source_Desc"].astype(str).str.strip()))

st.sidebar.header("Filters")
upstream_filter = st.sidebar.selectbox("Upstream System:", ["All"] + sorted(df["Upstream"].dropna().unique().tolist()))
product_filter = st.sidebar.selectbox("Product:", ["All"] + sorted(df["Product"].dropna().unique().tolist()))
target_filter = st.sidebar.selectbox("Target System:", ["All"] + sorted(df["Target"].dropna().unique().tolist()))

filtered_df = df.copy()
if upstream_filter != "All":
    filtered_df = filtered_df[filtered_df["Upstream"] == upstream_filter]
if product_filter != "All":
    filtered_df = filtered_df[filtered_df["Product"] == product_filter]
if target_filter != "All":
    filtered_df = filtered_df[filtered_df["Target"] == target_filter]

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

dot = graphviz.Digraph(format="svg")
dot.attr(rankdir="LR", fontname="Calibri", ratio="fill")


added_nodes = set()

def wrap_text(text, width=30):
    """Wrap text with <BR/> for Graphviz HTML-like labels."""
    return "<BR/>".join(textwrap.wrap(text, width=width))

def add_node(node, color):
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

    # header_lines = f"""
    # <B><FONT POINT-SIZE='20'>{node}</FONT></B><BR/>
    # <FONT POINT-SIZE='11'>{system_name}</FONT><BR/>
    # <FONT POINT-SIZE='10'>{desc}</FONT>
    # """

    # rows = f"""
    # <TR><TD ALIGN="CENTER" BORDER="1" SIDES="BOTTOM" CELLPADDING="4">{header_lines}</TD></TR>
    #"""

    header_lines = f"""
    <TABLE BORDER="0" CELLBORDER="0" CELLPADDING="1" CELLSPACING="0">
    <TR><TD ALIGN="CENTER"><B><FONT POINT-SIZE='10'>{node}</FONT></B></TD></TR>
    <TR><TD ALIGN="CENTER"><FONT POINT-SIZE='10'>{system_name}</FONT></TD></TR>
    <TR><TD ALIGN="CENTER"><FONT POINT-SIZE='10'>{desc}</FONT></TD></TR>
    </TABLE>
    """

    rows = f"""
    <TR><TD ALIGN="CENTER" BORDER="1" SIDES="BOTTOM" CELLPADDING="3" BALIGN="CENTER" VALIGN="MIDDLE">{header_lines}</TD></TR>
    """


    rows += """<TR><TD BORDER="0" BGCOLOR="black" HEIGHT="1" FIXEDSIZE="TRUE" WIDTH="100%"></TD></TR>"""

    if incoming:
        rows += """<TR><TD ALIGN="CENTER"><U><B><FONT POINT-SIZE="10">Product-In:</FONT></B></U></TD></TR>"""
        for p in incoming:
            wrapped = wrap_text(str(p), width=30)
            rows += f"""<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="10">{wrapped}</FONT></TD></TR>"""

    if outgoing:
        if incoming:
            rows += """<TR><TD BORDER="0" BGCOLOR="black" HEIGHT="1" FIXEDSIZE="TRUE" WIDTH="100%"></TD></TR>"""
        rows += """<TR><TD ALIGN="CENTER"><U><B><FONT POINT-SIZE="10">Product-Out:</FONT></B></U></TD></TR>"""
        for p in outgoing:
            wrapped = wrap_text(str(p), width=30)
            rows += f"""<TR><TD ALIGN="CENTER"><FONT POINT-SIZE="10">{wrapped}</FONT></TD></TR>"""

    label = f"""<
    <TABLE BORDER="1" CELLBORDER="0" CELLPADDING="5" CELLSPACING="0"
           ALIGN="CENTER" BGCOLOR="{color}">
        {rows}
    </TABLE>
    >"""

    dot.node(node, label=label, shape="none", fontsize="16", fontname="Arial")


for _, row in unique_edges.iterrows():
    s, c, t = row["Source"], row["Connection"], row["Target"]

    if s not in added_nodes:
        add_node(s, get_color(s))
        added_nodes.add(s)

    if t not in added_nodes:
        add_node(t, get_color(t))
        added_nodes.add(t)

    dot.edge(s, t, label=c)

st.graphviz_chart(dot, width="stretch")