# # import streamlit as st
# # import pandas as pd
# # import networkx as nx
# # from pyvis.network import Network
# # import os
# # import itertools
# # from matplotlib.colors import to_rgb, to_hex
# # import numpy as np

# # # File paths
# # input_excel = "Sooraj5.xlsx"
# # output_folder = "output_html"
# # os.makedirs(output_folder, exist_ok=True)

# # st.title("Resultant Product & Context Relationship Network Graph")

# # # Load Excel
# # try:
# #     df = pd.read_excel(input_excel, engine="openpyxl")
# # except Exception as e:
# #     st.error(f"Error reading Excel: {e}")
# #     st.stop()

# # required_cols = ["Product", "Context", "Source", "Relation", "Target"]
# # if not all(col in df.columns for col in required_cols):
# #     st.error(f"Excel must have columns: {required_cols}")
# #     st.stop()

# # # Sidebar filters
# # product_options = ["All"] + sorted(df["Product"].dropna().unique().tolist())
# # context_options = ["All"] + sorted(df["Context"].dropna().unique().tolist())

# # selected_product = st.sidebar.selectbox("Select Product", product_options)
# # selected_context = st.sidebar.selectbox("Select Context", context_options)

# # # Apply filters
# # filtered_df = df.copy()
# # if selected_product != "All" and selected_context != "All":
# #     filtered_df = df[(df["Product"] == selected_product) & (df["Context"] == selected_context)]
# # elif selected_product != "All":
# #     filtered_df = df[df["Product"] == selected_product]
# # elif selected_context != "All":
# #     filtered_df = df[df["Context"] == selected_context]

# # if filtered_df.empty:
# #     st.warning("No data found for the selected filters.")
# #     st.stop()

# # # --- Context Color Mapping (for Nodes) ---
# # context_color_map = {
# #     "Risk": "red",
# #     "Treasury": "green",
# #     "Finance": "blue"
# # }
# # default_node_color = "#0a5d7a"

# # # --- Relation-based color palette (for Edges/Arrows) ---
# # relation_types = filtered_df["Relation"].dropna().unique().tolist()
# # relation_color_list = [
# #     "#E74C3C", "#27AE60", "#2980B9", "#8E44AD", "#F39C12",
# #     "#16A085", "#2C3E50", "#D35400", "#7F8C8D", "#C0392B",
# #     "#9B59B6", "#1ABC9C"
# # ]
# # relation_color_cycle = itertools.cycle(relation_color_list)
# # relation_color_map = {rel: color for rel, color in zip(relation_types, relation_color_cycle)}

# # # --- Function to adjust color if too close to context color ---
# # def color_distance(c1, c2):
# #     """Compute Euclidean distance between two RGB colors."""
# #     return np.sqrt(np.sum((np.array(to_rgb(c1)) - np.array(to_rgb(c2))) ** 2))

# # def shift_color(color, factor=0.15):
# #     """Shift the color slightly by blending with white."""
# #     r, g, b = np.array(to_rgb(color))
# #     r = min(1, r + factor)
# #     g = min(1, g + factor)
# #     b = min(1, b + factor)
# #     return to_hex((r, g, b))

# # context_colors_rgb = [to_rgb(c) for c in context_color_map.values()]

# # # Adjust relation colors if too close to any context color
# # for rel, color in list(relation_color_map.items()):
# #     for ctx_color in context_color_map.values():
# #         if color_distance(color, ctx_color) < 0.25:  # similarity threshold
# #             relation_color_map[rel] = shift_color(color)
# #             break

# # # --- Build Directed Graph ---
# # G = nx.DiGraph()
# # for _, row in filtered_df.iterrows():
# #     G.add_edge(row["Source"], row["Target"], relation=row["Relation"], context=row["Context"])

# # # --- Determine Node Colors based on Context of Edges ---
# # node_contexts = {node: set() for node in G.nodes()}
# # for _, row in filtered_df.iterrows():
# #     src, tgt, ctx = row["Source"], row["Target"], row["Context"]
# #     node_contexts[src].add(ctx)
# #     node_contexts[tgt].add(ctx)

# # # Context priority: Risk > Treasury > Finance
# # def get_node_color(contexts):
# #     if "Risk" in contexts:
# #         return context_color_map["Risk"]
# #     elif "Treasury" in contexts:
# #         return context_color_map["Treasury"]
# #     elif "Finance" in contexts:
# #         return context_color_map["Finance"]
# #     else:
# #         return default_node_color

# # # --- Initialize PyVis Network ---
# # net = Network(height="750px", width="100%", bgcolor="#FFFFFF", directed=True, notebook=False)
# # net.toggle_physics(True)

# # # ⚙️ Updated options — added dotted edges (dashes: true)
# # net.set_options("""
# # var options = {
# #   "physics": {
# #     "barnesHut": {
# #       "gravitationalConstant": -3000,
# #       "centralGravity": 0.2,
# #       "springLength": 250,
# #       "springConstant": 0.02
# #     },
# #     "minVelocity": 0.75
# #   },
# #   "edges": {
# #     "font": {"multi": "html"},
# #     "smooth": {"type": "dynamic"},
# #     "arrows": {"to": {"enabled": true, "scaleFactor": 1.2}},
# #     "length": 250,
# #     "width": 4,
# #     "dashes": [2,1000]  
# #   }
# # }
# # """)
# # # the dashes property just above is for dotted arrow lines
# # # Compute degrees
# # outdegree_count = dict(G.out_degree())
# # indegree_count = dict(G.in_degree())

# # # --- Add Nodes ---
# # for node in G.nodes():
# #     out_count = outdegree_count.get(node, 0)
# #     in_count = indegree_count.get(node, 0)
# #     tooltip_text = f"{node} 🔸Incoming: {in_count} | 🔹Outgoing: {out_count}"
# #     color = get_node_color(node_contexts[node])
# #     net.add_node(
# #         node,
# #         label=node,
# #         title=tooltip_text,
# #         color=color,
# #         font={"color": "white", "size": 28},
# #         shape="box",
# #         borderWidth=4,
# #         shadow=True,
# #         size=250
# #     )

# # # --- Add Edges (colored by Relation, now dotted) ---
# # for u, v, data in G.edges(data=True):
# #     rel = data.get("relation", "")
# #     edge_color = relation_color_map.get(rel, "#808080")  # default grey
# #     relation_html = f"<b>{rel}</b>"
# #     net.add_edge(
# #         u,
# #         v,
# #         label=relation_html,
# #         color=edge_color,
# #         arrows="to",
# #         arrowStrikethrough=False,
# #         width=4,
# #         length=300,
# #         font={"multi": "html"},
# #         dashes=True  # 👈 ensures dotted style applies at edge level too
# #     )

# # # --- Save Graph ---
# # filter_name = f"{selected_product}_{selected_context}".replace("All", "AllData")
# # html_path = os.path.join(output_folder, f"{filter_name}_network.html")
# # net.save_graph(html_path)

# # # --- Legend Section ---
# # legend_html = """
# # <div style="background-color:#f2f2f2; padding:10px; border-radius:10px; margin-bottom:10px; font-size:16px;">
# #     <b>🗺️ Color Legend:</b><br>
# #     <u>Node Colors (At Context level):</u><br>
# #     <span style="color:blue; font-weight:bold;">⬤</span> Finance <br>
# #     <span style="color:red; font-weight:bold;">⬤</span> Risk <br>
# #     <span style="color:green; font-weight:bold;">⬤</span> Treasury <br><br>
# #     <i>All edges are now dotted (relation-based colors).</i><br>
# # </div>
# # """

# # st.markdown(legend_html, unsafe_allow_html=True)

# # # --- Display Graph in Streamlit ---
# # st.components.v1.html(open(html_path, "r", encoding="utf-8").read(), height=800, scrolling=True)

# # st.success(f"Resultant Network generated for Product: {selected_product}, Context: {selected_context}")



# import streamlit as st
# import pandas as pd
# import graphviz

# input_excel = "Sooraj5.xlsx"
# st.title("Resultant Product & Context Relationship Graph (Graphviz)")

# # Load Excel
# df = pd.read_excel(input_excel, engine="openpyxl")
# required_cols = ["Product", "Context", "Source", "Relation", "Target"]
# if not all(col in df.columns for col in required_cols):
#     st.error(f"Excel must have columns: {required_cols}")
#     st.stop()

# # Sidebar filters
# product_options = ["All"] + sorted(df["Product"].dropna().unique().tolist())
# context_options = ["All"] + sorted(df["Context"].dropna().unique().tolist())

# selected_product = st.sidebar.selectbox("Select Product", product_options)
# selected_context = st.sidebar.selectbox("Select Context", context_options)
# layout_dir = st.sidebar.radio("Graph Layout Direction", ["Left → Right", "Top → Bottom"])

# # Apply filters
# filtered_df = df.copy()
# if selected_product != "All":
#     filtered_df = filtered_df[filtered_df["Product"] == selected_product]
# if selected_context != "All":
#     filtered_df = filtered_df[filtered_df["Context"] == selected_context]

# if filtered_df.empty:
#     st.warning("No data found for selected filters.")
#     st.stop()

# # --- Group duplicate edges ---
# # Combine relations between same Source–Target pair
# grouped = (
#     filtered_df.groupby(["Source", "Target", "Context"])
#     .agg({"Relation": lambda x: ", ".join(sorted(set(x)))})
#     .reset_index()
# )

# # --- Graphviz settings ---
# graph_attr = {
#     "rankdir": "LR" if layout_dir == "Left → Right" else "TB",
#     "bgcolor": "white",
#     "splines": "spline",
#     "overlap": "false",
#     "fontsize": "12",
# }

# dot = graphviz.Digraph(comment="System Relationship Graph", graph_attr=graph_attr)
# dot.attr("node", shape="box", style="filled,rounded", fontname="Helvetica", fontsize="12")

# # --- Context colors ---
# context_color_map = {
#     "Risk": "lightcoral",
#     "Treasury": "lightgreen",
#     "Finance": "lightblue",
# }
# default_color = "#B0C4DE"

# # Add nodes and edges
# for _, row in grouped.iterrows():
#     ctx_color = context_color_map.get(row["Context"], default_color)
#     dot.node(row["Source"], style="filled", fillcolor=ctx_color)
#     dot.node(row["Target"], style="filled", fillcolor=ctx_color)
#     dot.edge(
#         row["Source"],
#         row["Target"],
#         label=row["Relation"],
#         fontsize="10",
#         color="gray40",
#         fontcolor="black"
#     )

# # Display Graphviz chart
# st.graphviz_chart(dot)
# st.success(f"✅ Cleaned Graph generated for Product: {selected_product}, Context: {selected_context}")



import streamlit as st
import base64

st.set_page_config(page_title="Secure Streamlit Portal", layout="centered")
st.title("🔐 Secure Streamlit Portal")


params = st.experimental_get_query_params()
encoded_data = params.get("data", [""])[0]

if not encoded_data:
    st.error("Invalid access. Please open this app through Power Apps.")
    st.stop()

try:
    decoded_email = base64.b64decode(encoded_data).decode("utf-8")
except Exception:
    st.error("Invalid or corrupted link.")
    st.stop()

st.write("Please verify your email to continue:")
user_email = st.text_input("Enter your company email:")

if st.button("Verify"):
    if not user_email:
        st.warning("Please enter your email.")
    elif user_email.strip().lower() == decoded_email.strip().lower():
        st.success(f"Access granted! Welcome, {user_email}")
        
        st.write("This is your secure content area.")
        st.write("You can now show dashboard, data, or reports here.")

    else:
        st.error("Email does not match. Access denied.")

