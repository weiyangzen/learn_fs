# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lruhash.h

Defines the LRU hash table data structures, callbacks, and API.

Key structures:
- `struct lruhash`: table lock, callback functions, bin array, LRU head/tail, entry count, memory counters, and collision stats.
- `struct lruhash_bin`: per-bin quick lock and overflow-chain head.
- `struct lruhash_entry`: entry rwlock, overflow link, LRU links, hash, key, and data.

Callback types:
- `lruhash_sizefunc_type`, `lruhash_compfunc_type`, `lruhash_delkeyfunc_type`, `lruhash_deldatafunc_type`, `lruhash_markdelfunc_type`.

Public API:
- Lifecycle: `lruhash_create`, `lruhash_delete`, `lruhash_clear`.
- Core operations: `lruhash_insert`, `lruhash_lookup`, `lruhash_remove`.
- LRU/memory control: `lru_touch`, `lru_demote`, `lruhash_update_space_used`, `lruhash_update_space_max`.
- Diagnostics/traversal: `lruhash_status`, `lruhash_get_mem`, `lruhash_traverse`.
- getdns-only helper: `lruhash_insert_or_retrieve`.
- Unit-test/internal helpers are exposed for bins, growth, reclaim, and LRU manipulation.

Concurrency contract:
- The header gives a detailed lock ordering strategy: table lock, bin lock, then entry lock.
- Callers must release entry locks after lookup.
- Callers must not hold locks on multiple hash entries acquired through separate normal lookups.
