# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_pctrie.c

## Purpose
Implements FreeBSD's path-compressed radix trie (`pctrie`) over 64-bit keys. It supports locked operations, SMR-protected unlocked lookups, iterators, range lookups, insertion, removal, replacement, and incremental reclamation.

## Main Interfaces
Lookup:
- `pctrie_lookup()`, `pctrie_lookup_unlocked()`.
- `pctrie_lookup_range()`, `pctrie_lookup_range_unlocked()`.
- `pctrie_lookup_ge()`, `pctrie_lookup_le()`, `pctrie_subtree_lookup_lt()`.

Iterator operations:
- `pctrie_iter_lookup()`, `pctrie_iter_lookup_range()`.
- `pctrie_iter_next()`, `pctrie_iter_prev()`, `pctrie_iter_stride()`.
- `pctrie_iter_lookup_ge()`, `pctrie_iter_lookup_le()`, jump variants.
- `pctrie_iter_remove()`, `pctrie_iter_value()`.

Mutation/reclaim:
- `pctrie_insert_lookup_strict()`, `pctrie_insert_lookup()`, `pctrie_iter_insert_lookup()`, `pctrie_insert_node()`.
- `pctrie_remove_lookup()`, `pctrie_replace()`.
- `pctrie_reclaim_begin/resume()` and callback variants.
- `pctrie_zone_init()`, `pctrie_node_size()`.

## Implementation Notes
Leaves are tagged pointers using `PCTRIE_ISLEAF`; interior nodes store owner prefix, compressed level, parent pointer, child popmap, and child array. `pn_popmap` records non-null children for locked traversal and mutation. SMR access uses `smr_entered_load()` and avoids relying on `pn_popmap` for consistency during unlocked range lookup.

Insertion first searches for the target; if a null leaf slot is found, it inserts directly. If an existing leaf/subtree conflicts, the caller allocates a branch node and `pctrie_insert_node()` computes the highest differing level, sets ownership, installs old/new children, and publishes the node with ordered SMR store semantics.

Removal compresses away interior nodes that become single-child. Reclamation walks and prunes subtries incrementally, optionally calling a callback for leaves.

## Dependencies
Uses `sys/pctrie.h`, SMR primitives, libkern bit helpers, DDB, and pointer-tagging contracts.

## Research Notes
This trie is relevant to VM and filesystem page/object indexes: it is optimized for sparse 64-bit key spaces and supports lockless readers where callers can provide SMR protection.
