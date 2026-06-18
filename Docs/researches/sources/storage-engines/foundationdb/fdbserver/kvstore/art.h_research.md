# sources/storage-engines/foundationdb/fdbserver/kvstore/art.h

## Purpose
This header declares an arena-backed adaptive radix tree used under `VersionedBTree`. It provides ordered key lookup, insertion, conditional insertion, deletion by iterator, and bidirectional iteration over linked leaves.

## Important APIs, Types, And Functions
`art_tree` defines node kinds `ART_LEAF`, `ART_NODE4/16/48/256`, and fat key-value variants `ART_NODE4_KV` through `ART_NODE256_KV`. Core structs are `art_node`, `art_leaf`, fixed-width child node structs, and fat-node wrappers that carry an exact-key `art_leaf*`. Public methods are `lower_bound`, `upper_bound`, `insert`, `insert_if_absent`, and `erase`. `art_iterator` exposes `operator++`, `operator--`, comparison, `key()`, `value()`, and `value_ptr()`.

## Control Flow
The tree starts with a sentinel `ART_NODE4` root, needed for empty keys. Private helpers implement prefix matching, minimum/maximum discovery, child search, iterative bound search, insertion splitting, node growth, deletion, and node shrinking.

## State And Persistence Behavior
All nodes and leaf key bytes are allocated from the caller-provided `Arena`. The tree stores raw `void*` values and does not own or persist them. Leaves are linked in sorted order using `prev` and `next`, so iterators traverse without rewalking the tree.

## Dependencies And Integration Points
The header depends on FoundationDB `KeyRef`, `Arena`, Flow platform intrinsics, and SSE comparison macros used by the implementation. It is tightly coupled to `art_impl.h`, which defines `VersionedBTree::art_tree` methods.

## Risks And Test Signals
The API is not type-safe around values and has no explicit end sentinel beyond null leaf iterators. Prefix compression, fat-node handling, and iterator link maintenance are correctness-critical. Tests should cover empty key insertion, prefix keys, lower/upper bounds, node fanout transitions, erase compaction, and iterator ordering.
