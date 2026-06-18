# sources/security-integrity/selinux/libsepol/cil/src/cil_tree.h

## Purpose

`cil_tree.h` defines the AST node shape and traversal API used by the CIL compiler.

## Important APIs, Types, and Functions

`struct cil_tree` stores the root node. `struct cil_tree_node` stores parent, child head/tail, next sibling, `enum cil_flavor`, line, HLL offset, and payload data. The header declares source-path helpers, logging, declaration detection, tree/node lifecycle, node removal, and `cil_tree_walk()`. It defines traversal skip flags: `CIL_TREE_SKIP_NOTHING`, `CIL_TREE_SKIP_NEXT`, `CIL_TREE_SKIP_HEAD`, and `CIL_TREE_SKIP_ALL`.

## Control Flow and Integration

`cil_tree_walk()` is the shared depth-first traversal primitive for resolver, resetter, and verifier passes. Callbacks can process nodes, observe entering/leaving child lists, and request branch skipping through the `finished` mask.

## State, Dependencies, and Risks

The header depends on `cil_flavor.h` and `cil_list.h`. It exposes raw tree structure, so callers can mutate links directly; that is powerful but risks parent/tail inconsistencies if not done carefully. Traversal skip constants are bit flags and must remain compatible with all walkers.

## Test Signals

Tests should compile users of the public struct layout, validate skip behavior, and verify lifecycle functions leave destroyed pointers null.
