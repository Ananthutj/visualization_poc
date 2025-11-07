# suppressPackageStartupMessages({
#   library(igraph)
#   library(ggplot2)
#   library(dplyr)
#   library(tidyr)
#   library(RColorBrewer)
# })

# # ---------------------------
# # Defensive checks
# # ---------------------------
# if (!exists("dataset")) stop("Input 'dataset' not found. Add fields to R visual input.")

# req_cols <- c("Source", "Target", "Relation", "Context")
# miss <- setdiff(req_cols, names(dataset))
# if (length(miss) > 0) stop(paste("Missing columns:", paste(miss, collapse = ", ")))

# # ---------------------------
# # Prepare data
# # ---------------------------
# edges <- dataset %>%
#   filter(!is.na(Source) & !is.na(Target) & !is.na(Relation)) %>%
#   mutate(
#     Source = toupper(trimws(Source)),
#     Target = toupper(trimws(Target)),
#     Relation = toupper(trimws(Relation)),
#     Context = toupper(trimws(Context))
#   ) %>%
#   group_by(Source, Target, Relation) %>%
#   summarise(Context = first(Context), .groups = "drop")

# if (nrow(edges) == 0) stop("No valid edges after filtering.")

# # ---------------------------
# # Create graph
# # ---------------------------
# g <- graph_from_data_frame(d = edges, directed = TRUE)

# # ---------------------------
# # Node colors
# # ---------------------------
# # ensure mapping is explicit: RISK -> red, TREASURY -> green, FINANCE -> blue
# context_colors <- c("RISK" = "red", "TREASURY" = "green", "FINANCE" = "blue")
# default_node_color <- "#b0c4de"

# node_context <- bind_rows(
#   edges %>% select(Node = Source, Context),
#   edges %>% select(Node = Target, Context)
# ) %>%
#   group_by(Node) %>%
#   summarise(Context = first(Context), .groups = "drop")

# V(g)$Context <- node_context$Context[match(V(g)$name, node_context$Node)]
# V(g)$color <- context_colors[V(g)$Context]
# V(g)$color[is.na(V(g)$color)] <- default_node_color

# # ---------------------------
# # Layout (Left-to-right)
# # ---------------------------
# set.seed(123)
# lay <- layout_with_sugiyama(g)$layout
# layout_df <- data.frame(
#   name = V(g)$name,
#   x = lay[, 2],
#   y = lay[, 1],
#   Context = V(g)$Context,         # <- add Context into layout_df (important)
#   fill = V(g)$color
# )
# layout_df$x <- max(layout_df$x) - layout_df$x
# layout_df$x <- layout_df$x - min(layout_df$x)

# # ---------------------------
# # Edge coordinates and offset
# # ---------------------------
# edge_df <- edges %>%
#   left_join(layout_df %>% select(Node = name, x, y), by = c("Source" = "Node")) %>%
#   rename(x = x, y = y) %>%
#   left_join(layout_df %>% select(Node = name, xend = x, yend = y), by = c("Target" = "Node")) %>%
#   group_by(Source, Target) %>%
#   mutate(
#     edge_count = n(),
#     edge_index = row_number(),
#     offset = (edge_index - (edge_count + 1) / 2) * 0.18,
#     label_vjust = ifelse(edge_index %% 2 == 0, -0.6, 1.2)
#   ) %>%
#   ungroup() %>%
#   mutate(y = y + offset, yend = yend + offset)

# # Shorten arrows slightly
# shrink <- 0.15
# edge_df <- edge_df %>%
#   mutate(
#     x_start = x + (xend - x) * shrink,
#     y_start = y + (yend - y) * shrink,
#     x_end = xend - (xend - x) * shrink,
#     y_end = yend - (yend - y) * shrink
#   )

# # ---------------------------
# # Relation colors
# # ---------------------------
# relation_types <- unique(edges$Relation)
# relation_colors <- setNames(
#   RColorBrewer::brewer.pal(min(length(relation_types), 8), "Dark2")[1:length(relation_types)],
#   relation_types
# )

# x_range <- range(layout_df$x)
# y_range <- range(layout_df$y)
# x_margin <- diff(x_range) * 0.05
# y_margin <- diff(y_range) * 0.05

# x_limits <- c(x_range[1] - x_margin, x_range[2] + x_margin)
# y_limits <- c(y_range[1] - y_margin, y_range[2] + y_margin)

# # ---------------------------
# # Plot (Power BI safe legend rendering)
# # ---------------------------
# p <- ggplot() +
#   geom_segment(
#     data = edge_df,
#     aes(x = x_start, y = y_start, xend = x_end, yend = y_end, color = Relation),
#     linewidth = 0.8,
#     arrow = arrow(length = unit(4, "mm"), type = "closed")
#   ) +
#   geom_text(
#     data = edge_df,
#     aes(x = (x_start + x_end)/2, y = (y_start + y_end)/2, label = Relation, color = Relation),
#     size = 3,
#     fontface = "bold",
#     vjust = -0.5
#   ) +
#   # Use the Context column from layout_df for fill mapping (data-driven)
#   geom_label(
#     data = layout_df,
#     aes(x = x, y = y, label = name, fill = Context),
#     color = "white",
#     size = 6,
#     fontface = "bold",
#     label.r = grid::unit(0.3, "lines"),
#     label.padding = grid::unit(0.4, "lines")
#   ) +
#   scale_color_manual(values = relation_colors, guide = "none") +

#   # Crucial: use explicit breaks so legend color <-> label match exactly
#   scale_fill_manual(
#     values = context_colors,
#     breaks = c("RISK", "TREASURY", "FINANCE"),
#     labels = c("RISK", "TREASURY", "FINANCE"),
#     name = "Context"
#   ) +

#   coord_cartesian(xlim = x_limits, ylim = y_limits, clip = "off") +
#   theme_void() +
#   theme(
#     plot.title = element_text(size = 11, face = "bold", hjust = 0.5),
#     legend.position = "bottom",
#     legend.title = element_text(face = "bold", size = 10),
#     legend.text = element_text(size = 9),
#     legend.key.size = unit(0.3, "cm"),
#     legend.spacing.x = unit(0.3, "cm"),
#     legend.box.spacing = unit(0.3, "cm")
#   ) +
# #   guides(
# #     fill = guide_legend(
# #       nrow = 1,
# #       byrow = TRUE,
# #       title.position = "top",
# #       override.aes = list(label = NA)  # remove any internal label drawing
# #     )
# #   )
# guides(
#   fill = guide_legend(
#     nrow = 1,
#     byrow = TRUE,
#     title.position = "top",
#     override.aes = list(
#       label = "",        # removes the "NA" text safely
#       colour = NA,       # remove white border
#       size = 5           # make legend keys clearly visible
#     )
#   )
# )


# print(p)






suppressPackageStartupMessages({
  library(igraph)
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(RColorBrewer)
})

# ---------------------------
# Defensive checks
# ---------------------------
if (!exists("dataset")) stop("Input 'dataset' not found. Add fields to R visual input.")

req_cols <- c("Source", "Target", "Relation", "Context")
miss <- setdiff(req_cols, names(dataset))
if (length(miss) > 0) stop(paste("Missing columns:", paste(miss, collapse = ", ")))

# ---------------------------
# Prepare data
# ---------------------------
edges <- dataset %>%
  filter(!is.na(Source) & !is.na(Target) & !is.na(Relation)) %>%
  mutate(
    Source = toupper(trimws(Source)),
    Target = toupper(trimws(Target)),
    Relation = toupper(trimws(Relation)),
    Context = toupper(trimws(Context))
  ) %>%
  group_by(Source, Target, Relation) %>%
  summarise(Context = first(Context), .groups = "drop")

if (nrow(edges) == 0) stop("No valid edges after filtering.")

# ---------------------------
# Create graph
# ---------------------------
g <- graph_from_data_frame(d = edges, directed = TRUE)

# ---------------------------
# Node colors
# ---------------------------
# ensure mapping is explicit: RISK -> red, TREASURY -> green, FINANCE -> blue
context_colors <- c("RISK" = "red", "TREASURY" = "green", "FINANCE" = "blue")
default_node_color <- "#b0c4de"

node_context <- bind_rows(
  edges %>% select(Node = Source, Context),
  edges %>% select(Node = Target, Context)
) %>%
  group_by(Node) %>%
  summarise(Context = first(Context), .groups = "drop")

V(g)$Context <- node_context$Context[match(V(g)$name, node_context$Node)]
V(g)$color <- context_colors[V(g)$Context]
V(g)$color[is.na(V(g)$color)] <- default_node_color

# ---------------------------
# Layout (Left-to-right)
# ---------------------------
set.seed(123)
lay <- layout_with_sugiyama(g)$layout
layout_df <- data.frame(
  name = V(g)$name,
  x = lay[, 2],
  y = lay[, 1],
  Context = V(g)$Context,         # <- add Context into layout_df (important)
  fill = V(g)$color
)
layout_df$x <- max(layout_df$x) - layout_df$x
layout_df$x <- layout_df$x - min(layout_df$x)

# ---------------------------
# Edge coordinates and offset
# ---------------------------
edge_df <- edges %>%
  left_join(layout_df %>% select(Node = name, x, y), by = c("Source" = "Node")) %>%
  rename(x = x, y = y) %>%
  left_join(layout_df %>% select(Node = name, xend = x, yend = y), by = c("Target" = "Node")) %>%
  group_by(Source, Target) %>%
  mutate(
    edge_count = n(),
    edge_index = row_number(),
    offset = (edge_index - (edge_count + 1) / 2) * 0.18,
    label_vjust = ifelse(edge_index %% 2 == 0, -0.6, 1.2)
  ) %>%
  ungroup() %>%
  mutate(y = y + offset, yend = yend + offset)

# Shorten arrows slightly
shrink <- 0.15
edge_df <- edge_df %>%
  mutate(
    x_start = x + (xend - x) * shrink,
    y_start = y + (yend - y) * shrink,
    x_end = xend - (xend - x) * shrink,
    y_end = yend - (yend - y) * shrink
  )

# ---------------------------
# Relation colors
# ---------------------------
relation_types <- unique(edges$Relation)
relation_colors <- setNames(
  RColorBrewer::brewer.pal(min(length(relation_types), 8), "Dark2")[1:length(relation_types)],
  relation_types
)

x_range <- range(layout_df$x)
y_range <- range(layout_df$y)
x_margin <- diff(x_range) * 0.05
y_margin <- diff(y_range) * 0.05

x_limits <- c(x_range[1] - x_margin, x_range[2] + x_margin)
y_limits <- c(y_range[1] - y_margin, y_range[2] + y_margin)

# ---------------------------
# Plot (Power BI safe legend rendering)
# ---------------------------
p <- ggplot() +
  geom_segment(
    data = edge_df,
    aes(x = x_start, y = y_start, xend = x_end, yend = y_end, color = Relation),
    linewidth = 0.8,
    arrow = arrow(length = unit(4, "mm"), type = "closed")
  ) +
  geom_text(
    data = edge_df,
    aes(x = (x_start + x_end)/2, y = (y_start + y_end)/2, label = Relation, color = Relation),
    size = 3,
    fontface = "bold",
    vjust = -0.5
  ) +
  # Use the Context column from layout_df for fill mapping (data-driven)
  geom_label(
    data = layout_df,
    aes(x = x, y = y, label = name, fill = Context),
    color = "white",
    size = 6,
    fontface = "bold",
    label.r = grid::unit(0.3, "lines"),
    label.padding = grid::unit(0.4, "lines")
  ) +
  scale_color_manual(values = relation_colors, guide = "none") +

  # Crucial: use explicit breaks so legend color <-> label match exactly
  scale_fill_manual(
    values = context_colors,
    breaks = c("RISK", "TREASURY", "FINANCE"),
    labels = c("RISK", "TREASURY", "FINANCE"),
    name = "Context"
  ) +

  coord_cartesian(xlim = x_limits, ylim = y_limits, clip = "off") +
  theme_void() +
  theme(
    plot.title = element_text(size = 11, face = "bold", hjust = 0.5),
    legend.position = "bottom",
    legend.title = element_text(face = "bold", size = 10),
    legend.text = element_text(size = 9),
    legend.key.size = unit(0.3, "cm"),
    legend.spacing.x = unit(0.3, "cm"),
    legend.box.spacing = unit(0.3, "cm")
  ) +
#   guides(
#     fill = guide_legend(
#       nrow = 1,
#       byrow = TRUE,
#       title.position = "top",
#       override.aes = list(label = NA)  # remove any internal label drawing
#     )
#   )
guides(
  fill = guide_legend(
    nrow = 1,
    byrow = TRUE,
    title.position = "top",
    override.aes = list(
      label = "",        # removes the "NA" text safely
      colour = NA,       # remove white border
      size = 5           # make legend keys clearly visible
    )
  )
)


print(p)



