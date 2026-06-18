# sources/security-integrity/selinux/libsepol/cil/src/cil_tree.c

## Purpose

`cil_tree.c` implements the CIL AST tree container, tree-node lifecycle, source-location logging, declarative-subtree detection, node removal, and depth-first traversal callbacks.

## Important APIs, Types, and Functions

Source helpers are `cil_tree_get_next_path()`, `cil_tree_get_cil_path()`, and `cil_tree_log()`. Lifecycle APIs include `cil_tree_init()`, `cil_tree_destroy()`, `cil_tree_subtree_destroy()`, `cil_tree_children_destroy()`, `cil_tree_node_init()`, `cil_tree_node_destroy()`, and `cil_tree_node_remove()`. Traversal is provided by `cil_tree_walk()` and internal `cil_tree_walk_core()`. `cil_tree_subtree_has_decl()` detects nodes with declarative flavors.

## Control Flow

Tree destruction recursively destroys children before destroying the node. Node destruction treats declarative datums specially: it removes the node from the datum's node list and destroys payload data only when the datum has no remaining nodes. Non-declarative nodes directly call `cil_destroy_data()`. `cil_tree_walk()` calls an optional `first_child` callback before descending into a child list, processes each child through `process_node`, respects `CIL_TREE_SKIP_NEXT` and `CIL_TREE_SKIP_HEAD`, recursively walks children, and calls `last_child` after a child list completes.

Source logging climbs parent/source metadata paths. It understands parse-tree `CIL_KEY_SRC_INFO` nodes, AST `CIL_SRC_INFO` nodes, and follows `CIL_CALL`/`CIL_BLOCKINHERIT` references back to macro or inherited block nodes to reconstruct user-facing source traces.

## State and Persistence Behavior

Each node stores parent, child head/tail, sibling next, flavor, CIL line, HLL offset, and payload pointer. Parent/child links are mutated by removal and child destruction. Logging does not alter tree state, but may traverse through resolved macro/blockinherit links. Node destruction also mutates symbol datum node lists.

## Dependencies and Integration Points

The tree layer depends on CIL internals, flavor names, list handling, parser/string conversion, string pool keys, and logging. It is the traversal backbone for reset, resolve, verification, build/copy, and cleanup passes.

## Risks and Test Signals

Destroy semantics are tied to declarative datum sharing; freeing too early would break aliases, inherited/copy nodes, or duplicate declarations, while failing to remove nodes leaks. `cil_tree_node_remove()` handles head/tail updates but assumes sibling links are valid. Traversal callbacks can mutate the tree, so pass code must be careful with delayed destruction. Tests should cover traversal skip flags, source trace generation through macros and blockinherit, node removal at head/tail/middle, declarative datum with multiple nodes, and recursive subtree destruction.
