# sources/user-network-fs/nfs-ganesha/src/hashtable/hashtable.c

## Purpose
This file implements Ganesha's generic concurrent hash table. The structure partitions keys across an array of red-black trees, locks each partition separately, stores opaque key/value buffer descriptors, and optionally accelerates repeated lookup with a small direct-mapped cache per partition.

## Important APIs, Types, And Functions
Public functions include `hashtable_init`, `hashtable_destroy`, `hashtable_acquire_latch`, `hashtable_getlatch`, `hashtable_releaselatched`, `hashtable_setlatched`, `hashtable_deletelatched`, `hashtable_delall`, `hashtable_log`, `hashtable_test_and_set`, `hashtable_getref`, `hashtable_for_each`, and `hash_table_err_to_str`. Internal helpers include `cache_page_size`, `cache_offsetof`, `compute`, and `key_locate`. Key types are `struct hash_table`, `struct hash_partition`, `struct hash_latch`, `struct hash_data`, `struct gsh_buffdesc`, and `rbt_node_t`.

## Control Flow, State, And Persistence
`compute` maps each key to a partition index and an RB-tree hash using either a combined hash callback or separate index/tree callbacks. `key_locate` checks the optional cache slot, validates actual key equality, then searches the partition RB tree for the leftmost matching hash and scans collisions until the exact key is found. `hashtable_getlatch` computes location, acquires a read or write lock, performs lookup, optionally returns the value, and either records latch state or unlocks on failure. `hashtable_setlatched` consumes a write latch, overwrites an existing descriptor or allocates pooled node/data objects and inserts into the partition tree. `hashtable_deletelatched` removes the latched node, clears cache, returns stored descriptors if requested, frees pooled storage, decrements count, and leaves the lock held for caller workflows that reuse the latch. `hashtable_delall` drains all trees partition by partition and invokes a caller-supplied free callback for stored contents.

## Dependencies And Integration Points
The implementation depends on `hashtable.h` contracts, Ganesha logging, atomic pointer operations, pthread rwlocks, memory/pool helpers, and RB-tree macros. Callers own the memory behind key/value buffer descriptors; the table stores descriptor pointers/lengths, not deep copies. Optional display callbacks integrate with debug logging.

## Risks And Test Signals
The latch API is powerful but easy to misuse: callers must match write/read intent, understand which calls release locks, and avoid using stale `latch->locator` after delete. `hashtable_delall` assumes `free_func` is non-null and successful; a failure exits with some entries already removed. Cache invalidation is coarse and disabled comparison by default, so cache correctness relies on clearing by hash slot during delete and exact-key validation during lookup. The `assert(*index < index_size)` protects hash functions only in assert-enabled builds.
