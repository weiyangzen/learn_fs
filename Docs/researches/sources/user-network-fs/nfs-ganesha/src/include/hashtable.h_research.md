# sources/user-network-fs/nfs-ganesha/src/include/hashtable.h

Purpose: This header declares Ganesha's concurrent non-intrusive hash table built from partitioned red-black trees with optional front-end caching.

Important APIs/types/functions: `struct hash_data` stores key/value `gsh_buffdesc` pairs. `struct hash_param` supplies hash, index, combined hash, comparison, display, naming, logging, and cache settings. `hash_stat_t`, `struct hash_partition`, `hash_table_t`, and `struct hash_latch` model table internals and latched lookup state. Public primitives include `hashtable_init`, destroy, get/acquire/release latch, set/delete latched, delete-all, logging, test-and-set, getref, and for-each. Inline wrappers `HashTable_Get`, `HashTable_Set`, and `HashTable_Del` implement common operations.

Control flow: Callers initialize with partition/hash functions, perform lookups by key, optionally latch a partition/tree position, then set/delete while holding latch state. Partitions use rwlocks; nodes and data come from pools.

State and persistence: In-memory table state includes per-partition counts, RBTs, locks, optional caches, and pooled key/value buffers. Stored buffer ownership is governed by caller/destructor callbacks.

Dependencies and integration points: Depends on RBT, pthreads, logging, display, memory pools, and `gsh_types.h`. Used by caches, duplicate request/state maps, and other keyed registries.

Risks: Hash function and comparator must agree or lookups fail. `HashTable_Set` defaults to no overwrite to avoid leaks. Latched paths require release on all outcomes. `HashTable_Del` fall-through behavior is intentional but easy to misread.

Test signals: Test create/destroy with destructors, get/set/delete success and missing-key paths, overwrite/no-overwrite/test-only behavior, latch release on errors, partition concurrency, cache-enabled lookup, stats/log display, and for-each traversal.
