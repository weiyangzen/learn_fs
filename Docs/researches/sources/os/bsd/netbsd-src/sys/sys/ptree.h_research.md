# File Research: sources/os/bsd/netbsd-src/sys/sys/ptree.h

## Purpose
Declares a generic Patricia/tree-like keyed node structure and operations with pluggable key matching/testing callbacks.

## Main API
- Direction enum: `PT_DESCENDING`, `PT_ASCENDING`.
- Types: `pt_slot_t`, `pt_bitoff_t`, `pt_bitlen_t`, `pt_node_t`, `pt_tree_ops_t`, `pt_tree_t`, `pt_filter_t`.
- Public functions: `ptree_init`, `ptree_insert_node`, `ptree_insert_mask_node`, `ptree_mask_node_p`, `ptree_find_filtered_node`, `ptree_find_node`, `ptree_remove_node`, `ptree_iterate`, `ptree_check`.
- Private macros under `_PT_PRIVATE` encode slot/type/nodedata/branchdata bitfields.

## Dependencies
Uses boolean and integer types when outside kernel/standalone.

## Risks and Notes
`pt_node_t` slots must be first, and private macros tag low pointer bits. Embedded nodes must satisfy alignment assumptions that leave type bits available. Tree behavior is driven by callback correctness.
