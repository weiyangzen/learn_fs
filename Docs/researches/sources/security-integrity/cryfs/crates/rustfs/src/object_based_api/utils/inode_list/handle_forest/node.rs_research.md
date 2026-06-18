# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/node.rs

Purpose: node record used inside `HandleForest`.

Important APIs: constructors `new_root` and `new`; parent accessors and `set_parent`; child lookup/insert/remove methods; `num_children`, `has_children`, `into_value`, `value`, `value_mut`; async drop; `RemoveResult`; `TryRemoveChildByHandleError`.

Control flow and state: stores optional `(parent_handle, edge_key)`, a child map from edge to handle, and an async-drop node value. Removal by handle verifies that the named edge points to the expected child and restores the mapping if it does not.

Dependencies and integration: generic over `HandleTrait`, edge key, and async-drop node value. Used only by `HandleForest`.

Risks and tests: `into_value` uses `unsafe_into_inner_dont_drop`, so callers must preserve drop responsibility. Parent and child bidirectional invariants are maintained by `HandleForest`, not this type alone.
