<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ts.c -->
# sources/object-store/daos/src/vos/tests/vts_ts.c

## Purpose
`vts_ts.c` tests VOS timestamp-set caching and the generic LRU array implementation used underneath it. It validates positive and negative timestamp cache entries across VOS timestamp types, eviction and reuse semantics, multi-level LRU array behavior, callback ordering, and stress behavior under deterministic pseudo-random allocation/eviction.

## Important APIs, Types, And Functions
`struct ts_test_arg` owns a temporary `vos_ts_set`, old global timestamp table, per-type record arrays, and count metadata copied from `vos_ts_table`. Timestamp tests call `vos_ts_table_alloc()`, `vos_ts_table_get()`, `vos_ts_table_set()`, `vos_ts_set_allocate()`, `vos_ts_set_reset()`, `vos_ts_lookup()`, `vos_ts_alloc()`, `vos_ts_get_negative()`, `vos_ts_evict()`, and `vos_ts_set_free()`.

The LRU tests use `lrua_array_alloc()`, `lrua_alloc()`, `lrua_allocx_inplace()`, `lrua_lookup()`, `lrua_lookupx()`, `lrua_evict()`, `lrua_evictx()`, `lrua_array_aggregate()`, and `lrua_array_free()`. `struct lru_record` embeds magic fields and a pointer back to an `index_record`; callbacks `on_entry_init()`, `on_entry_evict()`, and `on_entry_fini()` verify lifecycle transitions.

## Control Flow
`run_ts_tests()` runs four cmocka cases. `lru_array_test()` fills a single LRU array past capacity, verifies only the newest entries remain, touches one older surviving entry to protect it from eviction, then explicitly evicts it. `lru_array_stress_test()` repeatedly inserts and evicts under patterned frequencies, then runs a deterministic random sequence and a callback lookup scenario that targets a historical eviction bug. `lru_array_multi_test()` runs the same iteration against a multi-level array, aggregates it, and tests extended key lookup with inplace entries.

`ilog_test_ts_get()` first calls `run_positive_entry_test()` for every `VOS_TS_TYPE_*`. Positive tests allocate entries, verify lookups return identical objects, ensure parent type lookup before child allocation, and test LRU eviction/reuse. It then evicts all entries from child to parent order and runs `run_negative_entry_test()` to validate negative cache behavior, including special type-zero allocation and misses for all previous records.

## State And Persistence Behavior
The timestamp table and LRU arrays are in-memory acceleration structures, not persistent storage. State correctness matters because VOS incarnation-log and timestamp lookup paths can make decisions based on cached entries. The tests verify `ts_init_count` progression, type-specific capacities, parent-child lookup dependencies, LRU replacement, negative entry reuse after reset, and that evicted entries become unavailable until reallocated.

The LRU callback tests use magic values to ensure initialized records remain intact and evicted/finalized records update their source `index_record` to `MAGIC1`. Multi-level aggregation verifies that array compaction does not lose lookup or eviction semantics.

## Dependencies And Integration Points
The file integrates with `vts_io.h`, `vos_internal.h`, `vos_ts.h`, DAOS allocation/assertion utilities, DTX ID generation (`daos_dti_gen_unique()`), and the cmocka VOS test runner. It temporarily replaces the process-global timestamp table and restores it in `ts_test_fini()`, so it depends on proper isolation from other tests.

## Risks And Edge Cases
The largest local risk is memory pressure: `VOS_TS_SIZE` is 8 MiB per timestamp type of `uint32_t` records, plus the `BIG_TEST` stress allocation. The stress test fixes `srand(1)` because arbitrary seeds can fail this deterministic expectation suite. The timestamp tests assume the table's per-type counts are large enough for `NUM_EXTRA` and index 20 access. Global table replacement must always restore `old_table`; setup failure paths free only partially initialized state.

## Test Signals
Passing signals include exact LRU capacity retention, callback-driven magic transitions, safe lookup from inside eviction callbacks, successful multi-level `lrua_array_aggregate()`, correct extended-key misses/hits, timestamp `ts_init_count` expectations, positive lookup identity, negative lookup misses, and correct object reuse after explicit `vos_ts_evict()`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/tests/vts_ts.c -->
