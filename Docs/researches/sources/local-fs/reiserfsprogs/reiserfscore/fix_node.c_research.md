# File Research: sources/local-fs/reiserfsprogs/reiserfscore/fix_node.c

## Purpose
`fix_node.c` performs the pre-balance analysis for ReiserFS tree updates. Before insertion, paste, delete, or cut operations mutate the tree, it builds a virtual representation of the affected node, decides whether data can stay in place, shift to neighbors, merge, split, or require new blocks, and gathers the required parents, neighbors, and free buffers.

## Main Responsibilities
- Builds `struct virtual_node`/`struct virtual_item` state from the real path node.
- Computes how many items or bytes can move left/right.
- Handles direct, indirect, stat-data, and directory items with different split rules.
- Determines balancing parameters in `struct tree_balance`.
- Allocates free empty buffers for new nodes through `reiserfs_new_blocknrs`.
- Finds direct/far parents and neighboring nodes needed by later balancing.
- Cleans up path, neighbor, parent, and unused new-node buffers in `unfix_nodes`.

## Key Functions
- `create_virtual_node()` constructs virtual item metadata from `S[h]`, including item lengths, type flags, directory entry sizes, offsets, and left/right mergeability.
- `check_left()` / `check_right()` calculate how much of the virtual node can fit into left/right neighbors. Leaf splitting is constrained by 8-byte direct-item alignment, unformatted-pointer granularity, and whole directory entries.
- `get_num_ver()` estimates how many output nodes are needed under different shifting and flowing scenarios.
- `set_parameters()` writes the selected balancing plan into `tree_balance` fields such as `lnum`, `rnum`, `blknum`, `lbytes`, `rbytes`, `s0num`, `s1num`, and `s2num`.
- `are_items_mergeable()`, `is_left_mergeable()`, and `is_right_mergeable()` decide whether adjacent file/directory items can share a header after shifting.
- `get_parents()`, `get_far_parent()`, `get_direct_parent()`, and `get_neighbors()` resolve the path-relative parent/neighbor buffers used by execution code.
- `ip_check_balance()` handles increasing node size for insert/paste.
- `dc_check_balance_internal()` and `dc_check_balance_leaf()` handle decreasing node size for delete/cut.
- `fix_nodes()` is the public entry point; it walks levels bottom-up, computes plans, fetches resources, and propagates required insert sizes to higher levels.
- `unfix_nodes()` releases all resources and returns unused free blocks.

## Data and Control Flow
The file is the planning half of ReiserFS balancing. `fix_nodes()` starts at the leaf, validates the direct parent, initializes `tb->tb_vn`, and calls `check_balance()`. `check_balance()` sets virtual-node mode metadata and dispatches to insertion/paste or deletion/cut logic based on `tb->insert_size[h]`.

For leaf nodes, the analysis works in item/body units. Direct items can split only on 8-byte boundaries, indirect items on `UNFM_P_SIZE`, directory items only by complete directory entries, and stat-data or newly inserted empty directory items are not split. For internal nodes, the analysis works in fixed `DC_SIZE + KEY_SIZE` units.

The planner tries to minimize new node count, then minimize shifted neighbors, then prefer cached left neighbors. After a level is planned, `fix_nodes()` may allocate FEB buffers and compute the `insert_size` that must be propagated to the next tree level.

## Integration Points
- Calls `search_by_key`, `pathrelse`, `get_rkey`, `replace_key`-related helpers, and buffer-cache APIs.
- Supplies execution parameters consumed by `lbalance.c`, `ibalance.c`, and `do_balance.c`.
- Uses item/key helpers from `node_formats.c` and on-disk access macros from ReiserFS headers.
- Uses allocator functions such as `reiserfs_new_blocknrs()` and `reiserfs_free_block()`.

## Risks and Edge Cases
- The code relies heavily on path correctness and panics on inconsistent parent/child relationships.
- Directory splitting has special constraints for `.` and `..`; invalid counts can silently alter balance choices.
- `get_empty_nodes()` allocates blocks before final mutation and depends on `unfix_nodes()` to free unused FEB entries.
- Multiple comments reference historical kernel scheduling/SMP concerns, but this userspace implementation still assumes serialized buffer manipulation.
- Mergeability checks read neighbor leaves through tree searches; stale or corrupt paths can produce hard panics.

## Testing Signals
Good tests would cover insert/paste/delete/cut cases that trigger: no balancing, single-side shift, two-side shift, leaf merge/removal, internal merge/removal, root growth, root shrink, directory-entry splits, direct-item alignment, and indirect-pointer splits.
