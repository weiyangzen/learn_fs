# sources/user-network-fs/nfs-ganesha/src/include/rbt_node.h

## Purpose
This header defines the node and tree-head structures for Ganesha's red-black tree macros, adapted from STL red-black tree internals.

## Important APIs, Types, And Control Flow
`struct rbt_head` stores root, leftmost, rightmost, and node count. `rbt_node_t` stores flags, an `anchor` pointer-to-pointer, parent, left child, right child named `next`, sortable `uint64_t rbt_value`, and opaque user pointer `rbt_opaq`. `RBT_NUM` defines allocation batch size and `RBT_RED` marks red nodes.

## State And Persistence
The structures are embedded in caller-managed objects and hold in-memory tree linkage only. No persistence is defined.

## Dependencies And Integration Points
It depends on `<stdint.h>` and is consumed by `rbt_tree.h` macro algorithms and hashtable/cache structures that need ordered nodes.

## Risks And Test Signals
Because callers embed nodes, lifecycle misuse can corrupt arbitrary owner objects. Tests should verify initialization, duplicate values, unlink/reinsert behavior, opaque pointer retrieval, and memory ownership around embedded node containers.
