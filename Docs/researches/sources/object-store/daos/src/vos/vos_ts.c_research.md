# sources/object-store/daos/src/vos/vos_ts.c

Purpose: implements allocation, eviction, upgrade, and conflict checks for the VOS in-memory timestamp cache used by transactional read/write conflict detection.

Important APIs/functions: `vos_ts_table_alloc/free` allocate per-type LRU arrays and negative miss caches. `vos_ts_evict_lru` allocates or evicts an LRU entry and initializes it from global or negative timestamps. `vos_ts_set_allocate` creates an operation-local timestamp set when conditional operations or a real DTX require tracking. `vos_ts_set_upgrade` promotes negative entries to positive LRU entries after creates. `vos_ts_check_read_conflict` checks whether a write timestamp conflicts with recorded low/high read timestamps.

Control flow and state: cache state is memory-only in `vos_ts_table` and `vos_ts_entry`. On eviction, `ts_update_on_evict` pushes read timestamps and write timestamp cache data into the entry's negative cache or table-global state, preserving conservative conflict knowledge after the positive entry is reused. Allocation initializes miss entries from global start timestamps and creates LRU arrays for container, object, dkey, and akey levels. Timestamp sets record the transaction ID so same-epoch writes from a different DTX still conflict.

Dependencies/integration: depends on `vos_internal.h`, `vos_ts.h`, `lru_array`, DTX IDs, TLS telemetry allocation gauges, and VOS operation flags. Tree code and ilog paths populate timestamp sets as they walk object/key hierarchy.

Risks: correctness depends on negative-cache hashing and LRU eviction preserving conservative bounds; false sharing in negative entries is accepted, but missed updates would be dangerous. The conflict comparison treats equal epochs with different DTX IDs as conflicts. Non-transactional operations and non-conditional operations may skip allocation, so callers must pass correct flags.

Test signals: cover table allocation cleanup on partial failure, global-vs-negative eviction updates, conflict detection for lower/higher/equal epochs and same/different DTX IDs, negative entry upgrade after create, and memory gauge accounting.
