# sources/storage-engines/foundationdb/fdbserver/kvstore/art_impl.h

## Purpose
This header implements `VersionedBTree::art_tree`, an adaptive radix tree optimized for in-memory ordered key lookup in the kvstore path. It handles compressed prefixes, exact-prefix keys via fat nodes, variable fanout nodes, and sorted leaf iteration.

## Important APIs, Types, And Functions
Public methods implemented here are `insert`, `insert_if_absent`, `lower_bound`, `upper_bound`, and `erase`. Major helpers include `art_bound_iterative`, `check_bound_node`, `find_child`, `find_next`, `find_prev`, `minimum`, `maximum`, `minimum_kv`, `recursive_delete_binary`, `remove_child*`, `remove_fat_child*`, `iterative_insert`, `insert_leaf`, `insert_fat_node`, `insert_internal_node`, `insert_child`, `add_child*`, `alloc_node`, `alloc_kv_node`, `make_leaf`, `prefix_mismatch`, and linked-list helpers `insert_before`/`insert_after`.

## Control Flow
Bounds walk down compressed nodes, pushing backtracking frames into a static stack, then backtrack to the next greater subtree when no exact path exists. Insert descends until it finds a leaf, missing child, prefix mismatch, or key ending at an internal node. It then updates an existing leaf, splits a leaf, creates a fat node for a key that is a prefix of another key, splits an internal prefix, or adds a child. Deletion descends by prefix and child byte, removes a matching leaf or fat-node value, updates `prev`/`next`, and shrinks nodes from 256 to 48, 48 to 16, 16 to 4, or compresses single-child node4 paths.

## State And Persistence Behavior
Allocation is arena-only and never individually frees nodes. `size` is incremented by insert paths, though `insert_if_absent` appears to test `if (!existing)` rather than `if (!*existing)`, which is a suspicious size-accounting pattern. `erase` removes references and relinks leaves but does not reclaim arena memory. No on-disk persistence is performed.

## Dependencies And Integration Points
The file aliases `VersionedBTree::art_tree` and relies on definitions from `art.h`. It uses `KeyRef`, `Arena` placement allocation, Flow assertions, and platform bit operations such as `ctz`/`clz`; node16 search uses SSE intrinsics.

## Risks And Test Signals
`art_bound_iterative` uses a static `stack_entry arena[ART_MAX_KEY_LEN]`, explicitly single-threaded and risky for recursion-like reentrancy or very long keys. Raw casts and type tags must remain consistent with struct layout and fat-leaf offsets. Tests should stress prefix relations, long prefixes over `ART_MAX_PREFIX_LEN`, all node growth/shrink thresholds, lower/upper bound strictness, delete of fat leaves and ordinary leaves, empty root behavior, and iterator links after mutation.
