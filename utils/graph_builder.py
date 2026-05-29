import ast, os
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def build_dependency_graph(directory: str) -> nx.DiGraph:
    G = nx.DiGraph()
    for root, _, files in os.walk(directory):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            module = fname.replace(".py", "")
            G.add_node(module)
            try:
                with open(fpath, "r", errors="ignore") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                        for n in names:
                            G.add_edge(module, n.split(".")[0])
            except Exception:
                pass
    return G

def get_hotspots(G: nx.DiGraph, top_n=5) -> list[tuple]:
    in_deg = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)
    return in_deg[:top_n]

def export_graph_image(G: nx.DiGraph, output_path: str = "graph.png") -> str:
    # Guard: Handle repos with no nodes
    if G.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(12, 8), facecolor="#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        ax.text(0.5, 0.5, "No dependency data found.\nThis repo may be too small\nor contain no supported import statements.",
                ha="center", va="center", color="white", fontsize=12, transform=ax.transAxes)
        ax.axis("off")
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        return output_path
    
    # Determine figure size based on node count
    is_small_graph = G.number_of_nodes() < 5
    figsize = (8, 6) if is_small_graph else (12, 8)
    
    # Set up figure with dark theme
    fig, ax = plt.subplots(figsize=figsize, facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    
    # Calculate layout
    pos = nx.spring_layout(G, seed=42)
    
    # Determine node sizes based on in-degree: base 300 + in_degree * 200, minimum 800
    node_sizes = [max(800, 300 + G.in_degree(node) * 200) for node in G.nodes()]
    
    # Determine node colors based on in-degree thresholds
    node_colors = []
    for node in G.nodes():
        in_deg = G.in_degree(node)
        if in_deg > 5:
            node_colors.append("red")
        elif 3 <= in_deg <= 5:
            node_colors.append("yellow")
        else:
            node_colors.append("green")
    
    # Set font size based on graph size
    font_size = 14 if is_small_graph else 8
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#555555", arrows=True, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_color="white", ax=ax)
    
    # Set title and styling
    title = "Dependency Graph — CodeArchaeologist"
    if G.number_of_edges() == 0 and G.number_of_nodes() > 0:
        title += "\nNote: No import relationships detected between modules"
    
    ax.set_title(title, color="white", fontsize=14, pad=20)
    ax.axis("off")
    
    # Save the figure
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    
    return output_path