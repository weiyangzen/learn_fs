# sources/test-tools/strace/src/trie.c

Purpose: compact sparse trie mapping from up-to-64-bit integer keys to fixed-width values.

Important APIs/types/functions: `trie_create`, `trie_set`, `trie_get`, `trie_iterate_keys`, `trie_free`, `trie_get_node_size`, `trie_get_node_bit_offs`, `trie_get_node`, and packed data-block helpers.

Control flow: creation validates sizes, computes fill/empty values and depth. Lookup walks pointer nodes based on high-to-low key bit segments and optionally allocates nodes/data blocks. Leaf data blocks pack 1/2/4/8/16/32/64-bit values into `uint64_t` words. Iteration recursively visits existing nodes over an inclusive key range and invokes a callback for values.

State and persistence behavior: heap-allocated trie owns pointer nodes and data blocks; `trie_free` recursively frees all allocated nodes. No persistence outside memory.

Dependencies and integration points: depends on `macros.h` bit masks and `xmalloc.h`; useful for sparse maps inside strace subsystems.

Risks: bit arithmetic around 64-bit masks, inclusive range loops at `UINT64_MAX`, and value packing require careful boundary tests. `trie_set` masks stored values to item width.

Test signals: invalid create parameters, every item width, key size 64 and smaller, out-of-range keys, default empty value, overwrites, sparse allocation, iteration over empty/populated ranges, and freeing partially populated tries.
