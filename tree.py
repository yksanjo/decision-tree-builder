"""
Decision Tree core classes.

Provides decision tree structure with nodes, traversal, and execution.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum


class NodeType(Enum):
    """Type of decision node."""
    DECISION = "decision"      # Branch point with condition
    ACTION = "action"          # Execute an action
    LEAF = "leaf"              # Terminal node


@dataclass
class DecisionResult:
    """Result of a decision tree traversal."""
    path: list[str] = field(default_factory=list)
    outcome: Any = None
    reached_leaf: bool = False
    node_count: int = 0
    
    def add_step(self, node_id: str, outcome: Any = None) -> None:
        """Add a step to the path."""
        self.path.append(node_id)
        self.node_count += 1
        if outcome:
            self.outcome = outcome


@dataclass
class DecisionNode:
    """
    A node in the decision tree.
    
    Attributes:
        node_id: Unique identifier.
        node_type: Type of node (decision, action, leaf).
        question: Question/condition for decision nodes.
        action: Action to execute for action nodes.
        children: Child nodes keyed by answer/outcome.
        default_child: Default child if no match.
        metadata: Additional data for the node.
    """
    node_id: str
    node_type: NodeType = NodeType.DECISION
    question: Optional[str] = None
    action: Optional[Callable] = None
    children: dict[str, str] = field(default_factory=dict)
    default_child: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.node_type == NodeType.LEAF or not self.children
    
    def get_child(self, answer: str) -> Optional[str]:
        """Get child node ID for given answer."""
        if answer in self.children:
            return self.children[answer]
        return self.default_child


class DecisionTree:
    """
    A decision tree for structured decision making.
    
    Supports traversal with backtracking, caching, and visualization.
    
    Example:
        tree = DecisionTree(root=root_node)
        result = tree.traverse(context)
    """
    
    def __init__(self, root: Optional[DecisionNode] = None, name: str = "decision_tree"):
        """
        Initialize the decision tree.
        
        Args:
            root: Root node of the tree.
            name: Name of the tree.
        """
        self.name = name
        self.root = root
        self.nodes: dict[str, DecisionNode] = {}
        self._cache: dict[str, DecisionResult] = {}
        
        if root:
            self._index_node(root)
    
    def _index_node(self, node: DecisionNode) -> None:
        """Index a node and its children."""
        self.nodes[node.node_id] = node
        for child_id in node.children.values():
            if child_id and child_id in self.nodes:
                continue
            # This will be populated as nodes are added
    
    def add_node(self, node: DecisionNode) -> "DecisionTree":
        """Add a node to the tree."""
        self.nodes[node.node_id] = node
        return self
    
    def get_node(self, node_id: str) -> Optional[DecisionNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def set_root(self, node_id: str) -> "DecisionTree":
        """Set the root node."""
        node = self.get_node(node_id)
        if node is None:
            raise ValueError(f"Node '{node_id}' not found")
        self.root = node
        return self
    
    def traverse(
        self,
        context: Any,
        evaluator: Optional[Callable[[DecisionNode, Any], str]] = None,
        use_cache: bool = False
    ) -> DecisionResult:
        """
        Traverse the tree based on context.
        
        Args:
            context: Context data for evaluating conditions.
            evaluator: Function to evaluate decision nodes.
            use_cache: Whether to use cached results.
            
        Returns:
            DecisionResult with the traversal path.
        """
        if self.root is None:
            return DecisionResult(outcome="No root node")
        
        result = DecisionResult()
        
        if use_cache and str(context) in self._cache:
            return self._cache[str(context)]
        
        current = self.root
        max_depth = 100
        depth = 0
        
        while current and depth < max_depth:
            depth += 1
            result.add_step(current.node_id)
            
            # Execute action if action node
            if current.node_type == NodeType.ACTION and current.action:
                outcome = current.action(context)
                result.outcome = outcome
            
            # Check if leaf
            if current.is_leaf():
                result.reached_leaf = True
                break
            
            # Evaluate decision
            if evaluator:
                answer = evaluator(current, context)
            else:
                answer = self._default_evaluator(current, context)
            
            # Get next node
            next_node_id = current.get_child(answer)
            
            if next_node_id is None:
                break
            
            current = self.get_node(next_node_id)
        
        if use_cache:
            self._cache[str(context)] = result
        
        return result
    
    def _default_evaluator(self, node: DecisionNode, context: Any) -> str:
        """Default evaluator for decision nodes."""
        # Try to get attribute from context
        if hasattr(context, 'get'):
            # Dict-like
            for key in node.children.keys():
                if context.get(key):
                    return key
        
        # Try attribute access
        for key in node.children.keys():
            if hasattr(context, key) and getattr(context, key):
                return key
        
        # Return default or first child
        return node.default_child or list(node.children.keys())[0] if node.children else None
    
    def get_all_paths(self) -> list[list[str]]:
        """Get all possible paths from root to leaves."""
        if self.root is None:
            return []
        
        paths = []
        
        def dfs(node: DecisionNode, path: list[str]):
            path = path + [node.node_id]
            
            if node.is_leaf():
                paths.append(path)
            else:
                for child_id in node.children.values():
                    if child_id:
                        child = self.get_node(child_id)
                        if child:
                            dfs(child, path)
        
        dfs(self.root, [])
        return paths
    
    def clear_cache(self) -> None:
        """Clear the traversal cache."""
        self._cache.clear()
    
    def __repr__(self) -> str:
        return f"DecisionTree(name='{self.name}', nodes={len(self.nodes)})"
