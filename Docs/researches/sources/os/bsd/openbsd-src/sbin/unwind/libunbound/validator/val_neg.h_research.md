# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_neg.h

## Purpose
Declares aggressive negative-cache structures and APIs for validator denial-of-existence synthesis.

## Main Types
- `struct val_neg_cache`: shared locked cache with zone tree, LRU pointers, memory limits, NSEC3 iteration limit, and statistics counters.
- `struct val_neg_zone`: per-zone cache node with name/class, parent pointer, usage count, NSEC3 parameters, data tree, and in-use flag.
- `struct val_neg_data`: per-denial owner node with name, parent, count, zone pointer, LRU links, and in-use flag.

## Public API
- Lifecycle/memory: `val_neg_create`, `val_neg_get_mem`, `neg_cache_delete`, `val_neg_adjust_size`.
- Ordering: `val_neg_data_compare`, `val_neg_zone_compare`.
- Insertions: `val_neg_addreply`, `val_neg_addreferral`.
- Lookup/synthesis: `val_neg_getmsg`.
- Unit-test-exposed internals: `neg_insert_data`, `neg_delete_data`, `neg_find_zone`, `neg_create_zone`, `val_neg_zone_take_inuse`.

## Design Notes
The header explains the two-level tree design: zones hold NSEC data trees, while actual rrsets remain in the rrset cache. Parent placeholder nodes are intentionally stored to make insertion, deletion, and closest lookup logarithmic while preserving subtree counts.

## Integration
Used by the validator environment to opportunistically answer or prove negative results from already validated denial records.

## Notable Constraints
The cache is guarded by one coarse lock because rbtrees and LRU state are shared. This favors correctness and simple mutation semantics over fine-grained concurrency.
