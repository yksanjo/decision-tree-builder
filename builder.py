"""
Decision Tree Builder.

Provides a fluent API for building decision trees.
"""

from typing import Any, Callable, Optional
from .tree import DecisionTree, DecisionNode, NodeType


class TreeBuilder:
    """
    Fluent builder for creating decision trees.
    
    Example:
        builder = TreeBuilder()
        tree = builder.root("root", "Is it urgent?")
            .add_decision("yes", "handle_urgent")
            .add_decision("no", "handle_normal")
            .build()
    """
    
    def __init__(self, name: str = "decision_tree"):
        """
        Initialize the builder.
        
        Args:
            name: Name of the tree.
        """
        self.name = name
        self.nodes: dict[str, DecisionNode] = {}
        self.root_id: Optional[str] = None
    
    def root(
        self,
        node_id: str,
        question: str,
        description: str = ""
    ) -> "TreeBuilder":
        """
        Create the root node.
        
        Args:
            node_id: Unique identifier for the root.
            question: The decision question.
            description: Optional description.
            
        Returns:
            Self for chaining.
        """
        node = DecisionNode(
            node_id=node_id,
            node_type=NodeType.DECISION,
            question=question,
            metadata={"description": description}
        )
        self.nodes[node_id] = node
        self.root_id = node_id
        return self
    
    def add_decision(
        self,
        answer: str,
        next_node_id: str,
        question: str = ""
    ) -> "TreeBuilder":
        """
        Add a decision branch.
        
        Args:
            answer: The answer that leads to this branch.
            next_node_id: ID of the next node.
            question: Question for the next node.
            
        Returns:
            Self for chaining.
        """
        if not self.root_id:
            raise ValueError("Must create root node first")
        
        # Add the child node
        child = DecisionNode(
            node_id=next_node_id,
            node_type=NodeType.DECISION,
            question=question
        )
        self.nodes[next_node_id] = child
        
        # Connect from root
        self.nodes[self.root_id].children[answer] = next_node_id
        
        return self
    
    def add_action(
        self,
        node_id: str,
        action: Callable,
        answer: Optional[str] = None
    ) -> "TreeBuilder":
        """
        Add an action node.
        
        Args:
            node_id: Unique identifier.
            action: Action function to execute.
            answer: Optional answer that leads to this action.
            
        Returns:
            Self for chaining.
        """
        node = DecisionNode(
            node_id=node_id,
            node_type=NodeType.ACTION,
            action=action
        )
        self.nodes[node_id] = node
        
        if answer and self.root_id:
            self.nodes[self.root_id].children[answer] = node_id
        
        return self
    
    def add_leaf(
        self,
        node_id: str,
        outcome: Any,
        answer: Optional[str] = None
    ) -> "TreeBuilder":
        """
        Add a leaf node with outcome.
        
        Args:
            node_id: Unique identifier.
            outcome: The outcome value.
            answer: Optional answer that leads to this leaf.
            
        Returns:
            Self for chaining.
        """
        node = DecisionNode(
            node_id=node_id,
            node_type=NodeType.LEAF,
            metadata={"outcome": outcome}
        )
        self.nodes[node_id] = node
        
        if answer and self.root_id:
            self.nodes[self.root_id].children[answer] = node_id
        
        return self
    
    def connect(
        self,
        from_node_id: str,
        answer: str,
        to_node_id: str
    ) -> "TreeBuilder":
        """
        Connect two nodes.
        
        Args:
            from_node_id: Source node.
            answer: Answer that leads to destination.
            to_node_id: Destination node.
            
        Returns:
            Self for chaining.
        """
        if from_node_id not in self.nodes:
            raise ValueError(f"Node '{from_node_id}' not found")
        if to_node_id not in self.nodes:
            raise ValueError(f"Node '{to_node_id}' not found")
        
        self.nodes[from_node_id].children[answer] = to_node_id
        return self
    
    def set_default(self, from_node_id: str, to_node_id: str) -> "TreeBuilder":
        """
        Set default branch.
        
        Args:
            from_node_id: Source node.
            to_node_id: Default destination.
            
        Returns:
            Self for chaining.
        """
        if from_node_id not in self.nodes:
            raise ValueError(f"Node '{from_node_id}' not found")
        
        self.nodes[from_node_id].default_child = to_node_id
        return self
    
    def build(self) -> DecisionTree:
        """
        Build the decision tree.
        
        Returns:
            DecisionTree instance.
        """
        if not self.root_id:
            raise ValueError("Must create root node first")
        
        root = self.nodes[self.root_id]
        tree = DecisionTree(root=root, name=self.name)
        
        # Add all nodes
        for node_id, node in self.nodes.items():
            tree.add_node(node)
        
        return tree
