"""
Decision Tree Visualizer.

Provides visualization utilities for decision trees.
"""

from typing import Optional
from .tree import DecisionTree, DecisionNode, NodeType


class TreeVisualizer:
    """
    Visualizer for decision trees.
    
    Provides text and ASCII visualization of tree structures.
    
    Example:
        visualizer = TreeVisualizer()
        print(visualizer.to_text(tree))
        print(visualizer.to_ascii(tree))
    """
    
    def __init__(self, indent_size: int = 2):
        """
        Initialize the visualizer.
        
        Args:
            indent_size: Number of spaces per indent level.
        """
        self.indent_size = indent_size
    
    def to_text(self, tree: DecisionTree) -> str:
        """
        Generate text representation of the tree.
        
        Args:
            tree: Decision tree to visualize.
            
        Returns:
            String representation of the tree.
        """
        lines = [f"Decision Tree: {tree.name}", "=" * 50]
        
        if tree.root is None:
            lines.append("(empty tree)")
            return "\n".join(lines)
        
        lines.append(f"\nRoot: {tree.root.node_id}")
        lines.append(f"Nodes: {len(tree.nodes)}")
        
        lines.append("\nNode Details:")
        lines.append("-" * 50)
        
        for node_id, node in tree.nodes.items():
            node_type = node.node_type.value
            lines.append(f"\n[{node_id}] ({node_type})")
            
            if node.question:
                lines.append(f"  Question: {node.question}")
            
            if node.action:
                lines.append(f"  Action: {node.action.__name__}")
            
            if node.metadata.get("outcome"):
                lines.append(f"  Outcome: {node.metadata.get('outcome')}")
            
            if node.children:
                lines.append(f"  Children:")
                for answer, child_id in node.children.items():
                    lines.append(f"    {answer} -> {child_id}")
            
            if node.default_child:
                lines.append(f"    default -> {node.default_child}")
        
        return "\n".join(lines)
    
    def to_ascii(self, tree: DecisionTree) -> str:
        """
        Generate ASCII tree representation.
        
        Args:
            tree: Decision tree to visualize.
            
        Returns:
            ASCII representation of the tree.
        """
        if tree.root is None:
            return "(empty tree)"
        
        lines = []
        self._render_node(tree.root, tree, "", True, lines)
        return "\n".join(lines)
    
    def _render_node(
        self,
        node: DecisionNode,
        tree: DecisionTree,
        prefix: str,
        is_last: bool,
        lines: list
    ) -> None:
        """Recursively render a node."""
        # Determine connector
        connector = "└── " if is_last else "├── "
        
        # Node label
        if node.node_type == NodeType.LEAF:
            label = f"🎯 {node.node_id}"
            if node.metadata.get("outcome"):
                label += f" = {node.metadata.get('outcome')}"
        elif node.node_type == NodeType.ACTION:
            label = f"⚡ {node.node_id}"
        else:
            label = f"❓ {node.node_id}"
        
        if node.question:
            label += f"\n{prefix}   {node.question[:50]}..."
        
        lines.append(f"{prefix}{connector}{label}")
        
        # Children
        if node.children:
            child_items = list(node.children.items())
            for i, (answer, child_id) in enumerate(child_items):
                is_last_child = i == len(child_items) - 1
                child = tree.get_node(child_id)
                
                if child:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    self._render_node(child, tree, new_prefix, is_last_child, lines)
    
    def to_mermaid(self, tree: DecisionTree) -> str:
        """
        Generate Mermaid diagram code.
        
        Args:
            tree: Decision tree to visualize.
            
        Returns:
            Mermaid diagram code.
        """
        lines = ["graph TD"]
        
        for node_id, node in tree.nodes.items():
            # Node definition
            if node.node_type == NodeType.LEAF:
                shape = f'{node_id}["{node_id}'
                if node.metadata.get("outcome"):
                    shape += f": {node.metadata.get('outcome')}"
                shape += '"]'
            elif node.node_type == NodeType.ACTION:
                shape = f'{node_id}["{node_id}'
                if node.question:
                    shape += f": {node.question[:30]}..."
                shape += '"]'
            else:
                shape = f'{node_id}{{"{node_id}'
                if node.question:
                    shape += f": {node.question[:30]}..."
                shape += '}}'
            
            lines.append(f"    {shape}")
            
            # Edges
            for answer, child_id in node.children.items():
                safe_answer = answer.replace('"', "'")
                lines.append(f"    {node_id} -- {safe_answer} --> {child_id}")
        
        return "\n".join(lines)
    
    def to_dot(self, tree: DecisionTree) -> str:
        """
        Generate DOT (Graphviz) diagram code.
        
        Args:
            tree: Decision tree to visualize.
            
        Returns:
            DOT diagram code.
        """
        lines = [
            "digraph decision_tree {",
            "    rankdir=TB;",
            "    node [shape=box];",
        ]
        
        for node_id, node in tree.nodes.items():
            # Node style
            if node.node_type == NodeType.LEAF:
                lines.append(f'    "{node_id}" [shape=ellipse, style=filled, fillcolor=lightgreen];')
            elif node.node_type == NodeType.ACTION:
                lines.append(f'    "{node_id}" [shape=diamond, style=filled, fillcolor=lightyellow];')
            else:
                lines.append(f'    "{node_id}" [shape=box];')
            
            # Edges
            for answer, child_id in node.children.items():
                safe_answer = answer.replace('"', '\\"')
                lines.append(f'    "{node_id}" -> "{child_id}" [label="{safe_answer}"];')
        
        lines.append("}")
        return "\n".join(lines)
