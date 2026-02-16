"""
Demo examples for the Decision Tree Builder.

Demonstrates building and traversing decision trees.
"""

from decision_tree_builder import (
    DecisionTree,
    DecisionNode,
    DecisionResult,
    TreeBuilder,
    TreeVisualizer,
)
from decision_tree_builder.tree import NodeType


# =============================================================================
# Example 1: Basic Decision Tree
# =============================================================================

def demo_basic_tree():
    """Demonstrate basic decision tree creation and traversal."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Decision Tree")
    print("=" * 60)
    
    # Create nodes manually
    root = DecisionNode(
        node_id="root",
        node_type=NodeType.DECISION,
        question="Is it urgent?",
        children={"yes": "handle_urgent", "no": "handle_normal"}
    )
    
    handle_urgent = DecisionNode(
        node_id="handle_urgent",
        node_type=NodeType.ACTION,
        action=lambda ctx: "Escalated to priority queue"
    )
    
    handle_normal = DecisionNode(
        node_id="handle_normal",
        node_type=NodeType.LEAF,
        metadata={"outcome": "Standard processing"}
    )
    
    # Build tree
    tree = DecisionTree(root=root, name="urgent_classifier")
    tree.add_node(handle_urgent)
    tree.add_node(handle_normal)
    
    # Traverse
    context = {"is_urgent": True}
    result = tree.traverse(context)
    
    print(f"Tree: {tree}")
    print(f"Context: {context}")
    print(f"Result: path={result.path}, outcome={result.outcome}")


# =============================================================================
# Example 2: Using Tree Builder
# =============================================================================

def demo_builder():
    """Demonstrate using the fluent builder API."""
    print("\n" + "=" * 60)
    print("Example 2: Tree Builder")
    print("=" * 60)
    
    # Define actions
    def escalate_action(ctx):
        print("[Action] Escalating to manager")
        return "Escalated"
    
    def process_action(ctx):
        print("[Action] Processing normally")
        return "Processed"
    
    def auto_action(ctx):
        print("[Action] Auto-resolving")
        return "Auto-resolved"
    
    # Build tree using builder
    tree = (
        TreeBuilder(name="support_ticket")
        .root("root", "What is the priority?")
        .add_decision("high", "high_priority", "Is it a security issue?")
        .add_decision("medium", "medium_priority", "Can it wait?")
        .add_decision("low", "low_priority", "Is it a feature request?")
        
        # High priority branch
        .add_action("handle_high", escalate_action, "yes")
        .connect("high_priority", "no", "medium_priority")
        
        # Medium priority branch
        .add_action("handle_medium", process_action, "yes")
        .connect("medium_priority", "no", "low_priority")
        
        # Low priority branch
        .add_leaf("handle_feature", "Feature logged", "yes")
        .add_leaf("handle_bug", "Bug fixed", "no")
        
        .build()
    )
    
    # Visualize
    viz = TreeVisualizer()
    print(viz.to_text(tree))
    print("\nASCII View:")
    print(viz.to_ascii(tree))


# =============================================================================
# Example 3: Custom Evaluator
# =============================================================================

def demo_custom_evaluator():
    """Demonstrate custom evaluator function."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Evaluator")
    print("=" * 60)
    
    # Define a more complex tree
    root = DecisionNode(
        node_id="root",
        node_type=NodeType.DECISION,
        question="What type of request?",
        children={
            "refund": "refund_flow",
            "complaint": "complaint_flow",
            "inquiry": "inquiry_flow"
        }
    )
    
    refund_flow = DecisionNode(
        node_id="refund_flow",
        node_type=NodeType.DECISION,
        question="Is within return period?",
        children={"yes": "approve_refund", "no": "deny_refund"}
    )
    
    complaint_flow = DecisionNode(
        node_id="complaint_flow",
        node_type=NodeType.ACTION,
        action=lambda ctx: "Customer service contacted"
    )
    
    inquiry_flow = DecisionNode(
        node_id="inquiry_flow",
        node_type=NodeType.LEAF,
        metadata={"outcome": "Information provided"}
    )
    
    approve_refund = DecisionNode(
        node_id="approve_refund",
        node_type=NodeType.LEAF,
        metadata={"outcome": "Refund approved"}
    )
    
    deny_refund = DecisionNode(
        node_id="deny_refund",
        node_type=NodeType.LEAF,
        metadata={"outcome": "Refund denied - outside period"}
    )
    
    # Build tree
    tree = DecisionTree(root=root, name="customer_service")
    for node in [refund_flow, complaint_flow, inquiry_flow, approve_refund, deny_refund]:
        tree.add_node(node)
    
    # Custom evaluator
    def custom_evaluator(node, context):
        """Evaluate based on request_type in context."""
        request_type = context.get("request_type", "")
        
        if node.node_id == "root":
            return request_type
        elif node.node_id == "refund_flow":
            return "yes" if context.get("within_period", False) else "no"
        
        return "yes"
    
    # Test cases
    test_cases = [
        {"request_type": "refund", "within_period": True},
        {"request_type": "refund", "within_period": False},
        {"request_type": "complaint"},
        {"request_type": "inquiry"},
    ]
    
    for context in test_cases:
        result = tree.traverse(context, evaluator=custom_evaluator)
        print(f"Context: {context}")
        print(f"Path: {result.path}, Outcome: {result.outcome}\n")


# =============================================================================
# Example 4: Visualization Formats
# =============================================================================

def demo_visualization():
    """Demonstrate different visualization formats."""
    print("\n" + "=" * 60)
    print("Example 4: Visualization Formats")
    print("=" * 60)
    
    # Build a simple tree
    tree = (
        TreeBuilder(name="simple_flow")
        .root("start", "Is it working?")
        .add_action("yes", "celebrate", lambda ctx: "Success!")
        .add_action("no", "debug", lambda ctx: "Debugging...")
        .build()
    )
    
    viz = TreeVisualizer()
    
    print("Text Format:")
    print(viz.to_text(tree))
    
    print("\n" + "-" * 40)
    print("Mermaid Format:")
    print(viz.to_mermaid(tree))
    
    print("\n" + "-" * 40)
    print("DOT Format:")
    print(viz.to_dot(tree))


# =============================================================================
# Example 5: Path Analysis
# =============================================================================

def demo_path_analysis():
    """Demonstrate path analysis features."""
    print("\n" + "=" * 60)
    print("Example 5: Path Analysis")
    print("=" * 60)
    
    # Build tree with multiple paths
    tree = (
        TreeBuilder(name="multi_path")
        .root("root", "Choose path")
        .add_decision("a", "node_a", "Continue A?")
        .add_decision("b", "node_b", "Continue B?")
        .add_decision("c", "node_c", "Continue C?")
        
        .add_leaf("leaf_a1", "Outcome A1", "yes")
        .connect("node_a", "no", "node_b")
        
        .add_leaf("leaf_b1", "Outcome B1", "yes")
        .connect("node_b", "no", "node_c")
        
        .add_leaf("leaf_c1", "Outcome C1", "yes")
        .build()
    )
    
    # Get all paths
    paths = tree.get_all_paths()
    print(f"Total paths: {len(paths)}")
    for i, path in enumerate(paths):
        print(f"  Path {i+1}: {' -> '.join(path)}")


# =============================================================================
# Run All Demos
# =============================================================================

if __name__ == "__main__":
    demo_basic_tree()
    demo_builder()
    demo_custom_evaluator()
    demo_visualization()
    demo_path_analysis()
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
