# sources/user-network-fs/nfs-ganesha/src/gtest/test_rbt.cc

## Purpose
This benchmark-style GoogleTest measures red-black-tree lookup, removal, and insertion throughput for a sliding window of RPC-like transaction IDs. It is not tied to FSAL exports; it targets Ganesha's `opr_rbtree` infrastructure.

## Important APIs, Types, And Functions
`struct rbt_item` embeds `opr_rbtree_node`, stores a `uint32_t xid`, and includes a 64 KiB pad to reduce cache friendliness. `rbt_item_xid_cmpf` compares embedded xids. `RBTLatency1` allocates `item_wsize` entries, initializes `call_replies` with `opr_rbtree_init`, and inserts the initial window. The test uses `opr_rbtree_lookup`, `opr_rbtree_remove`, and `opr_rbtree_insert`.

## Control Flow, State, And Persistence
Setup fills a tree with 100,000 sequential xids. `RUN1` performs one million iterations: look up the oldest xid, remove it, update that item to the next xid, reinsert it, and advance both counters. Timing covers only this sliding-window loop. Teardown deletes the allocated array.

## Dependencies And Integration Points
The file includes Ganesha core headers, `misc/rbtree_x.h`, queue/intrinsic helpers, LTTng, and gperftools. Optional profiling is controlled by the namespace-local `profile_out` pointer, currently null.

## Risks And Test Signals
The lookup result is not checked for null before `opr_containerof`, so tree corruption or lookup failure will crash. The reported `fprintf` format appears to provide fewer arguments than format specifiers for the final `reqs/s` message, which is a correctness risk in diagnostics. The main signal is timing and process survival under heavy tree mutation.
