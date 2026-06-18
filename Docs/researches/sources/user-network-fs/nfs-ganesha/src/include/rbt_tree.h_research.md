# sources/user-network-fs/nfs-ganesha/src/include/rbt_tree.h

## Purpose
This macro-only header implements red-black tree operations over `struct rbt_head` and `struct rbt_node` for ordered in-memory indexes.

## Important APIs, Types, And Control Flow
Macros include `RBT_HEAD_INIT`, `RBT_COUNT`, `RBT_RIGHTMOST`, `RBT_LEFTMOST`, `RBT_VALUE`, `RBT_OPAQ`, forward/reverse iteration with `RBT_INCREMENT`, `RBT_DECREMENT`, `RBT_LOOP`, and `RBT_LOOP_REVERSE`, rotations, `RBT_INSERT`, `RBT_UNLINK`, `RBT_FIND`, `RBT_FIND_LEFT`, `RBT_BLACK_COUNT`, and `RBT_VERIFY`. Insert and unlink mutate anchors, parent/child links, leftmost/rightmost cache pointers, count, and red/black flags.

## State And Persistence
All state is caller-owned in-memory tree linkage. The macros perform no allocation, locking, or persistence; callers must provide initialized heads/nodes and external synchronization.

## Dependencies And Integration Points
It relies on `rbt_node.h` definitions being available. The macros are intended for low-level caches/hashtables where function-call overhead or generic containers are avoided.

## Risks And Test Signals
The macro implementation evaluates arguments with side effects, dereferences sibling pointers in unlink fix-up, and has no built-in locking. Duplicate key handling is supported but subtle. Tests should exercise empty trees, ordered and random inserts, duplicate keys, deletion of root/leaf/two-child nodes, iteration after mutations, reverse iteration, `RBT_VERIFY` error detection, and sanitizer runs for pointer misuse.
