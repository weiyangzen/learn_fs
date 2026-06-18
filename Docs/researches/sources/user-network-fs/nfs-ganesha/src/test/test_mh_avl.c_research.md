# sources/user-network-fs/nfs-ganesha/src/test/test_mh_avl.c

Purpose: CUnit test for using an AVL tree as a hash-key index with Murmur3-derived keys and probing.

Important APIs, types, and functions: `avl_unit_val_t` stores two AVL nodes, a `{k, p}` hash/probe key, a name, and an FSAL cookie. `qp_avl_insert` hashes names with `MurmurHash3_x64_128`, attempts quadratic probing, then linear probing. `qp_avl_lookup_s` repeats the probe sequence and compares names. Tests insert a fixed dir listing and then 100000 synthetic file names.

Control flow: the first phase inserts and looks up static file names. The second inserts `file0` through `file99999` and looks up `file0` through `file199999`, aborting on misses for the first half. Cleanup removes all nodes and frees duplicated names.

State and persistence: one global AVL tree contains heap nodes and duplicated strings during each suite run.

Dependencies and integration points: depends on CUnit, `avltree`, `murmur3`, and Ganesha memory wrappers. CMake includes `../support/murmur3.c` in this target.

Risks: `qp_avl_lookup_s` is called with `maxj == 1`, so it will not find entries that needed probing even though insert supports probing. Probe loops use `uint32_t j < UINT64_MAX`, which is effectively unbounded and type-mismatched. Lookup allocates many temporary `avl_unit_val_t` objects in a loop but only frees the last one, leaking test memory. `avl_unit_clear_tree` always removes from `avl_tree_1`.

Test signals: catches common no-collision lookup and large insert behavior, but collision/probing behavior is under-tested and memory usage is noisy.
