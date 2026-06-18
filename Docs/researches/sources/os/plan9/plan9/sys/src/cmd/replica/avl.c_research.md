# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/avl.c

Read status: complete, 415 lines.

This file implements an in-memory AVL tree used by the replica database. It provides rotations, insertion, lookup, deletion, predecessor/successor walking, and iterator adjustment when nodes are deleted during traversal.

The tree stores caller-owned structs containing an embedded `Avl` node. `insertavl` replaces equal keys and returns the old node. `deleteavl` invokes `walkdel` so active `Avlwalk` iterators remain usable when their current node is deleted.

Traversal uses `avlwalk`, `avlnext`, `avlprev`, and `endwalk`. The database code relies on reverse traversal while deleting entries.

Filesystem relevance: indirect but important. It indexes replica path metadata efficiently while tools scan and mutate filesystem state.
