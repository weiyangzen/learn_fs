# sources/object-store/daos/src/vos/ilog.c

## Purpose
Implements VOS incarnation logs for object/key create/update/punch history. It records epoch plus DTX/minor-epoch identity, resolves committed/uncommitted/removed status through callbacks, persists/aborts transaction entries, fetches cached log state for visibility checks, and aggregates obsolete entries.

## Important APIs, Types, And Functions
Public APIs include `ilog_init`, `ilog_create`, `ilog_open`, `ilog_close`, `ilog_destroy`, `ilog_update`, `ilog_set_flags`, `ilog_persist`, `ilog_abort`, `ilog_fetch_*`, `ilog_aggregate`, `ilog_is_corrupted`, `ilog_ts_idx_get`, `ilog_version_get`, `ilog_root_is_valid`, and `ilog_is_valid`. Key internals are `struct ilog_context`, `struct ilog_array_cache`, `struct ilog_priv`, `ilog_modify`, `ilog_tree_modify`, `ilog_root_migrate`, `update_inplace`, `remove_entry`, `reset_root`, `ilog_status_refresh`, and aggregation helpers.

## Control Flow
`ilog_create` writes a valid magic/version root. `ilog_open` wraps a root and callbacks in a handle. Updates build an `ilog_id` and call `ilog_modify`, which handles flag updates, empty inline insert, inline update/remove, migration to an allocated sorted array on the second distinct entry, and array insertion/removal for larger logs. Persist clears the transaction id for the matching entry; abort removes it. Fetch initializes or reuses `ilog_entries` cache when root pointer and version match, refreshing statuses by intent. Aggregation fetches entries, classifies them with parent punch/discard/in-progress state, marks removals, collapses arrays, and may reduce the root back to inline or empty.

## State And Persistence
The durable root is exactly `struct ilog_df` sized and stores magic/version/flags, timestamp index, and either inline `ilog_id` or an allocated `ilog_array`. Version bits change on mutations so callers can cache safely. All persistent writes go through `umem` transactions and undo logging. DTX registration/deregistration is delegated through callback hooks.

## Dependencies And Integration
Depends on DAOS/VOS types, `umem`, `vos_layout`, `vos_ts`, DTX helpers, and `ilog_internal.h`. Higher layers wrap it through `vos_ilog.h` for object/key visibility, punches, timestamp cache entries, and corruption failout.

## Risks
The header comment still says B+tree fallback, but the current implementation uses a dynamically resized array; readers should not infer B-tree behavior. Correctness depends on sorted epoch order, version updates, callback status semantics, and no same-epoch conflicting DTX mutations. Fixed-epoch mode intentionally relaxes equality checks for rebuild/aggregation-style operations. `ilog_fetch_finish` frees dynamic status arrays but not root-owned ids. Aggregation aborts on uncommitted entries unless discarding in-progress entries.

## Test Signals
VOS test harness references `run_ilog_tests`. Expected test coverage includes inline-empty/one-entry/multi-entry transitions, persist/abort callback behavior, fetch cache invalidation by version and intent, discard/in-progress aggregation, corrupted flag handling, and `ilog_is_valid` recovery checks.
