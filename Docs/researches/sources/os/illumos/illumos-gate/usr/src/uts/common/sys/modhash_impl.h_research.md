# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/modhash_impl.h

Purpose: Defines internal structures and helpers for the generic kernel hash implementation.

Key structures:
- `mod_hash_entry`: key/value and chain pointer.
- `mod_hash_stat`: hit, miss, collision, element, and allocation-failure counters.
- `mod_hash`: rwlock, name, allocation behavior, chain count, destructors, comparator, hash algorithm, private algorithm data, global-list link, stats, and flexible chain array.

Key macros/APIs:
- `MH_SIZE(n)` computes allocation size for a hash with `n` chains.
- `mod_hash_init()`.
- Internal no-sync routines for hash, insert, remove, find, walk, clear.

Important detail: No-sync routines are internal and require callers to handle locking correctly.

Relevance to subset A: Generic utility internals.
