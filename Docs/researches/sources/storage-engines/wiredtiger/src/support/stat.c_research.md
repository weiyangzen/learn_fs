# Research: sources/storage-engines/wiredtiger/src/support/stat.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008995`: lines 1-4527, `Docs/researches/chunks/subset-b-008995_research.md`
- `subset-b-008996`: lines 4528-5363, `Docs/researches/chunks/subset-b-008996_research.md`

## Chunk Research

### subset-b-008995: lines 1-4527

# sources/storage-engines/wiredtiger/src/support/stat.c lines 1-4527

## Chunk Scope

This chunk is the generated front portion of WiredTiger's statistic support implementation. It starts with the `DO NOT EDIT: automatically built by dist/stat.py` banner, includes `wt_internal.h`, defines the full data-source statistic description table, implements data-source statistic initialization, clearing, and aggregation, then defines the connection statistic description table and implements connection statistic initialization and clearing. The chunk ends in the early cache/capacity section of `__wt_stat_connection_aggregate`; the rest of connection aggregation and the later session-stat helpers are outside this work item.

The researched span is `sources/storage-engines/wiredtiger/src/support/stat.c:1-4527`.

## Purpose

The file gives WiredTiger's statistics cursor and internal monitoring paths a generated mapping between stable statistic slots, human-readable descriptions, and concrete `int64_t` fields in generated statistic structures. It also provides the lifecycle helpers that allocate per-slot statistic arrays, reset clearable counters, and aggregate per-session/per-handle counters into a single visible result.

The chunk covers two statistic families:

- Data-source statistics for a `WT_DATA_HANDLE`, including btree shape, block manager, cache, cursor, layered table, reconciliation, rollback-to-stable, and transaction counters.
- Connection statistics for a `WT_CONNECTION_IMPL`, including global versions of many data-source counters plus background compaction, backup, block cache, connection, capacity, checkpoint, cursor sweep, data-handle, disaggregated, live-restore, load-control, lock, log, perf histogram, prefetch, session, thread, tiered, and transaction counters.

Because this file is generated, the durable API contract is not the hand-written C logic but the generated slot ordering and descriptions that must stay synchronized with `src/include/stat.h` and public statistic ids.

## Important APIs, Types, and Data Structures

### Description tables

`__stats_dsrc_desc[]` maps every data-source statistic slot to the string returned by a `statistics:` cursor. The table includes categories such as `autocommit`, `backup`, `block-disagg`, `block-manager`, `btree`, `cache`, `cache_walk`, `checkpoint-cleanup`, `checkpoint`, `compression`, `cursor`, `layered`, `reconciliation`, `session`, and `transaction`.

`__stats_connection_desc[]` performs the same role for connection statistics. Its categories are broader and include connection-only systems such as background compaction, block cache, capacity, data-handle sweeping, live restore, load control, lock manager, logging, performance histograms, prefetch, thread-state, thread-yield, and tiered storage.

The accessors `__wt_stat_dsrc_desc` and `__wt_stat_connection_desc` ignore the cursor argument and return `desc[slot]` through an output pointer. They assume the caller has already bounded `slot` with the cursor's statistic count.

### Statistic storage

`WT_DSRC_STATS` and `WT_CONNECTION_STATS` are generated structures in `src/include/stat.h`. That header documents that statistic structures are treated as arrays of `int64_t`, allowing macros to translate a field name into a slot offset.

Both statistic families use 23 counter slots:

- `WT_STAT_DSRC_COUNTER_SLOTS`
- `WT_STAT_CONN_COUNTER_SLOTS`

Each session writes to a slot derived from its session id (`session->id % slot_count`). This reduces write contention without requiring per-CPU ids. Reads aggregate all slots by field offset.

`WT_DATA_HANDLE` stores:

- `WT_DSRC_STATS *stats[WT_STAT_DSRC_COUNTER_SLOTS]`
- `WT_DSRC_STATS *stat_array`

`WT_CONNECTION_IMPL` stores the analogous connection arrays.

### Data-source functions

- `__wt_stat_dsrc_init_single(WT_DSRC_STATS *stats)` zeroes one data-source stat struct with `memset`.
- `__wt_stat_dsrc_init(WT_SESSION_IMPL *session, WT_DATA_HANDLE *handle)` allocates `WT_STAT_DSRC_COUNTER_SLOTS` contiguous structs with `__wt_calloc`, stores each element address in `handle->stats[i]`, and zeroes it.
- `__wt_stat_dsrc_discard(WT_SESSION_IMPL *session, WT_DATA_HANDLE *handle)` frees `handle->stat_array`.
- `__wt_stat_dsrc_clear_single(WT_DSRC_STATS *stats)` resets generated clearable fields and intentionally leaves current-state or high-water fields untouched, annotated with `/* not clearing ... */`.
- `__wt_stat_dsrc_clear_all(WT_DSRC_STATS **stats)` clears every per-session slot by calling `__wt_stat_dsrc_clear_single`.
- `__wt_stat_dsrc_aggregate_single(WT_DSRC_STATS *from, WT_DSRC_STATS *to)` merges one already-materialized source struct into `to`.
- `__wt_stat_dsrc_aggregate(WT_DSRC_STATS **from, WT_DSRC_STATS *to)` reads and sums across all per-slot structs using `WT_STAT_DSRC_READ`.

### Connection functions

- `__wt_stat_connection_init_single(WT_CONNECTION_STATS *stats)` zeroes one connection stat struct.
- `__wt_stat_connection_init(WT_SESSION_IMPL *session, WT_CONNECTION_IMPL *handle)` allocates and initializes the connection stat slots.
- `__wt_stat_connection_discard(WT_SESSION_IMPL *session, WT_CONNECTION_IMPL *handle)` frees the contiguous connection stat array.
- `__wt_stat_connection_clear_single(WT_CONNECTION_STATS *stats)` resets clearable counters while preserving gauges, configuration values, current states, min/max/recent timing fields, and other persistent observability values.
- `__wt_stat_connection_clear_all(WT_CONNECTION_STATS **stats)` clears every connection stat slot.
- `__wt_stat_connection_aggregate(WT_CONNECTION_STATS **from, WT_CONNECTION_STATS *to)` begins at line 4017. In this chunk it aggregates from autocommit through `capacity_bytes_log`; the function continues after line 4527.

## Control Flow

Initialization is simple and allocation-driven. The owner (`WT_DATA_HANDLE` or `WT_CONNECTION_IMPL`) calls the generated init routine, which allocates one contiguous array sized by the generated slot count. The pointer array is then populated with addresses into that allocation. If allocation fails, `WT_RET` returns the error before any later setup.

Statistics writes happen elsewhere in WiredTiger through macros and subsystem code. This file's main runtime paths are read/reset paths:

1. Statistics cursors call the description function for a slot to expose the stable textual name.
2. If a cursor requests current values, cursor/stat code points at the relevant `WT_*_STATS` struct or an aggregate buffer.
3. For multi-slot owners, aggregate helpers add each field from all slots into a single output struct. Data-source aggregation is complete in this chunk; connection aggregation begins here and continues later.
4. If statistics are opened with clear semantics, clear helpers reset only counters that are meant to restart from zero.

The aggregation functions are deliberately mechanical. Most fields use addition. Some scalar configuration or high-water fields use a maximum merge, for example data-source `allocation_size`, block version fields, btree page-size limits, maximum tree depth, `rec_multiblock_max`, and connection fields such as `npos_evict_walk_max`, `cache_hazard_max`, and `npos_read_walk_max`.

## State and Persistence Behavior

This code manages in-memory observability state only. It does not write WiredTiger metadata, table data, logs, or checkpoints directly.

The state model is nevertheless important:

- Per-slot arrays are persistent for the lifetime of their owning connection or data handle and are released through the matching discard routine.
- Clear routines intentionally do not fully zero the structures. Gauges, current states, configured limits, recent/min/max timings, and some cumulative state remain visible across a clear operation.
- Aggregation is race-tolerant rather than transactional. `src/include/stat.h` notes that summing per-slot `int64_t` counters can race with concurrent writers; negative aggregate results are clamped to zero for API compatibility.
- Statistic ordering is externally visible through statistic cursor slots and `WT_STAT_*` ids. Reordering fields or descriptions without regenerating all related artifacts would break callers that depend on stable ids.

Persistence relevance is indirect. Many counters describe persistent subsystems such as block allocation, checkpoint, history store, recovery, logging, rollback-to-stable, tiered storage, and disaggregated metadata. The counters report those systems' behavior, but their values are not themselves durable state.

## Dependencies and Integration Points

Direct dependencies include:

- `wt_internal.h`, which brings in all WiredTiger internal types, allocation helpers, stat macros, and generated declarations.
- `src/include/stat.h`, which defines slot counts, field-offset macros, read/write macros, clear flags, generated `WT_CONNECTION_STATS` and `WT_DSRC_STATS`, and public statistic base ids.
- `__wt_calloc`, `__wt_free`, `WT_RET`, and `WT_UNUSED`.
- Generated extern declarations in `src/include/extern.h`.

Runtime integration points include:

- `src/cursor/cur_stat.c`, which sets statistic cursor bases/counts and exposes connection/data-source stats to users.
- `src/schema/schema_stat.c`, which builds data-source statistic cursor views.
- `src/conn/conn_stat.c`, which gathers connection-level stats.
- Subsystems that write fields through statistic macros, including block managers, btree tree-walk stats, cache/eviction, reconciliation, transaction/rollback-to-stable, cursor operations, checkpoint, logging, tiered/disaggregated storage, live restore, and lock/load-control code.
- Data-handle and connection lifecycle code, which owns when the generated init/discard helpers are called.

## Risks and Maintenance Notes

- The file is generated by `dist/stat.py`; manual edits will be overwritten and can desynchronize descriptions, structures, public ids, and aggregate/clear behavior.
- The description arrays must match generated struct field order exactly. An off-by-one slot bug would surface as statistics cursors returning the wrong name for a value.
- Clear semantics are encoded as generated assignments and `not clearing` omissions. Misclassifying a field changes user-visible behavior for statistics opened with clear/reset options.
- Aggregation semantics are per-field. Counters usually sum, but gauges/high-water/configuration fields often need max or preservation semantics. Generator changes that turn max fields into sums can produce misleading observability data.
- Aggregation reads race with writers by design. This is acceptable for approximate statistics but unsuitable for code that would rely on these helpers for correctness decisions.
- The assigned chunk ends mid-`__wt_stat_connection_aggregate`; any final per-file research must merge this note with later chunks to describe the full connection aggregation function and session stat helpers.

## Test Signals

Useful validation signals for this chunk are statistics-cursor and generated-file consistency tests:

- Opening `statistics:` and `statistics:<uri>` cursors should return stable ids, descriptions, and values for connection and data-source stats.
- Statistics opened with clear behavior should reset clearable counters while preserving current-state gauges and documented high-water/configuration values.
- Workloads that exercise cursor operations, cache eviction, checkpoint, reconciliation, rollback-to-stable, logging, backup, tiered storage, disaggregated storage, and live restore should show expected non-zero counters in their matching categories.
- Multi-session workloads should verify aggregation across per-session slots, not just one writer slot.
- Generated drift checks should rerun `dist/stat.py` and verify `src/support/stat.c`, `src/include/stat.h`, and generated extern declarations remain synchronized.

### subset-b-008996: lines 4528-5363

# sources/storage-engines/wiredtiger/src/support/stat.c lines 4528-5363

## Scope

This chunk covers the tail of WiredTiger's generated statistics support file. The range starts inside `__wt_stat_connection_aggregate`, at the connection-stat aggregation entries for capacity throttling, and runs through the end of that function. It then defines the session-stat descriptor table and the small helper routines for session statistic lookup, initialization, and clear/reset behavior.

`stat.c` is generated by `dist/stat.py` and begins with a `DO NOT EDIT` marker. The code in this chunk should therefore be treated as generated glue between the canonical statistics metadata and runtime statistic structures, not as hand-maintained business logic.

## Purpose

The connection-stat portion adds per-slot connection statistics from a source array into an aggregate destination `WT_CONNECTION_STATS`. WiredTiger keeps connection statistics in multiple slots, and `WT_STAT_CONN_READ(from, field)` reads the aggregate value for one named field across those slots. `__wt_stat_connection_aggregate` then adds that value into `to->field`, allowing callers to combine multiple statistic sources into one connection-level view.

The session-stat portion exposes descriptions and lifecycle helpers for `WT_SESSION_STATS`. Session stats are much smaller than connection stats and are read directly from one `WT_SESSION_STATS` structure. The chunk maps each session-stat slot to a stable human-readable string, zeros a session stats block on initialization, and clears the resettable session counters while intentionally preserving transaction-local counters.

## Important APIs, Types, and Data

- `__wt_stat_connection_aggregate(WT_CONNECTION_STATS **from, WT_CONNECTION_STATS *to)`: this function begins before the chunk and ends at line 5319. Lines 4528-5318 are a long sequence of `to->field += WT_STAT_CONN_READ(from, field)` assignments.
- `WT_STAT_CONN_READ(stats, fld)`: macro from `src/include/stat.h` that resolves a field offset and calls `__wt_stats_aggregate_conn`; it is the key dependency for reading a named connection statistic from a slot array.
- `WT_CONNECTION_STATS`: generated struct containing all connection-level counters. This chunk references many fields spanning capacity, checkpoint, cursor, handle, disaggregation, layered table, live restore, locks, logging, histograms, prefetch, reconciliation, session operation, application wait, tiered storage, and transaction families.
- `__stats_session_desc[]`: static const descriptor table for the 11 generated session statistics. Its order must match `struct __wt_session_stats` and the exported `WT_STAT_SESSION_*` slot constants.
- `__wt_stat_session_desc(WT_CURSOR_STAT *cst, int slot, const char **p)`: stores `__stats_session_desc[slot]` in `*p` and returns success. `cst` is unused because session descriptions are globally static.
- `__wt_stat_session_init_single(WT_SESSION_STATS *stats)`: clears the whole session stats struct with `memset`.
- `__wt_stat_session_clear_single(WT_SESSION_STATS *stats)`: clears resettable session counters individually while leaving `txn_bytes_dirty` and `txn_updates` intact.
- `WT_SESSION_STATS`: generated struct with fields `bytes_read`, `bytes_write`, `lock_dhandle_wait`, `txn_bytes_dirty`, `txn_updates`, `read_time`, `write_time`, `lock_schema_wait`, `cache_time`, `cache_time_interruptible`, and `cache_time_mandatory`.

## Connection Aggregation Covered Here

The aggregation sequence is mechanical and has no branches in this chunk: every listed connection field is read from `from` and added into the matching field in `to`. Important stat families covered by this range include:

- Capacity throttling and I/O budgeting: bytes read/written by checkpoint, eviction, log, and read paths, threshold counters, and time spent in capacity enforcement.
- Checkpoint and checkpoint-cleanup: cleanup duration, pages visited/read/removed/evicted, obsolete time-window handling, skipped pages, snapshot acquisition, fsync/post-sync duration, checkpoint generations, per-handle checkpoint timing and counts, scrub/prep/sync timing, total success/failure counts, and reconciliation work during checkpoint.
- General connection and cursor activity: condition waits, data handle counts and sweeps, file/btree opens, memory allocation/free/grow counters, low-level read/write/fsync I/O, cursor bounds/search/insert/modify/remove/update/reset/reopen counters, cursor error counters, and cursor open timing.
- Data-handle and sweep state: connection handle counts by kind, handle size/count, dead/expired close counts, sweep skip reasons, session handle counts, and session sweep counts.
- Disaggregated and layered storage: disaggregated checkpoint abandon/apply/pick-up/role/step timing stats, layered cursor operations split across ingest/stable views, layered table manager checkpoint/logop stats, truncate-list GC/search stats, and disaggregated block-manager histogram fields.
- Live restore and workload admission: bytes copied, work remaining, source-read count and latency buckets, live-restore state, read/write reject counts, and read/write load values.
- Locking and logging: btree page/checkpoint/dhandle/metadata/schema/table/transaction-global lock wait/count fields, log payload/written bytes, compression stats, scans, LSN publication, sync durations, slot races/yields/closes, preallocation, buffer/compression sizing, and close yields.
- Performance histograms: block-manager read/write, disaggregated block-manager read/write, filesystem read/write, internal/leaf reconstruct, operation read/write latency buckets, and total elapsed time accumulators.
- Prefetch: skip reasons, attempts, queued/read/failure pages, and successful attempt counts.
- Reconciliation and page image/delta accounting: variable-length column-store empty pages, time-window bytes, page modification histograms, history-store wrapup calls, full-image and delta counts, multiblock/overflow output, maximum reconciliation timings, page-delta rejection reasons, page size buckets, prepared/timestamped/transactional pages, aggregate time-window values, split-stash counters, and skipped writes.
- Session operation counters promoted into connection stats: session open/query timestamp and table alter/compact/create/drop/publish/salvage/truncate/verify success and failure families.
- Application wait and blocked-page counters: application cache operations and time split into interruptible/uninterruptible, eviction snapshot refreshes, transaction release/dhandle/page/ref/prepared/page-busy/page-read/page-sleep blockage, rollback-blocked deletes, child-modify blockage, split restarts, and deleted-page read skips.
- Tiered storage and transactions: local object in-use/removed, flush-tier outcomes, tiered work unit lifecycle, tiered retention, prepared update outcomes, prepare/commit/rollback/query timestamp counters, rollback-to-stable dry-run and live counters, timestamp set/global/pinned values, transaction begin/commit/rollback, and update conflicts.

Because the destination uses `+=`, callers can build an aggregate from several source statistic arrays or add into an already partially populated destination. Correctness depends on the caller zeroing `to` when a fresh aggregate is desired.

## Session Statistic Behavior

`__stats_session_desc[]` contains the external descriptions returned by session statistics cursors:

- bytes read into cache and bytes written from cache
- dhandle and schema lock wait time
- dirty bytes and update count in the current transaction
- page read/write time
- cache wait time split into total, interruptible eviction, and mandatory eviction

`__wt_stat_session_init_single` performs a full reset with `memset`, suitable when creating or reinitializing a session stats structure. `__wt_stat_session_clear_single` is intentionally narrower: it resets I/O, lock wait, read/write timing, and cache wait fields but does not clear `txn_bytes_dirty` or `txn_updates`. That preservation matters because those counters describe the currently active transaction, and clearing general session statistics must not hide in-flight transaction state.

## Control Flow

The connection aggregation path in this chunk is straight-line generated code. For each statistic, it:

1. Calls `WT_STAT_CONN_READ(from, field)`.
2. Adds the returned value to `to->field`.
3. Moves to the next generated field.

There are no local conditionals, loops, allocations, locks, error checks, or early exits in this range. Synchronization and multi-slot aggregation behavior are delegated to the statistic read macro and its helper.

The session helpers are also direct:

- `__wt_stat_session_desc` indexes the descriptor array by `slot`, writes the pointer into `p`, and returns `0`.
- `__wt_stat_session_init_single` zeros `sizeof(*stats)`.
- `__wt_stat_session_clear_single` assigns zero to selected fields, with comments documenting the two retained transaction counters.

## State and Persistence

All state touched here is in-memory diagnostic state. The code does not write WiredTiger metadata, table files, log files, checkpoints, or durable configuration. It aggregates values already maintained elsewhere by runtime subsystems.

The connection aggregation is additive and non-destructive with respect to `from`. The destination `to` is mutated by incrementing many `int64_t` fields. Session initialization and clearing mutate a single `WT_SESSION_STATS` object in place. Descriptor strings are static read-only process data.

Persistence implications are indirect: many counters describe persistent operations such as checkpoint, logging, reconciliation, rollback-to-stable, and tiered object management, but this chunk only reports or resets statistic values. It does not perform those operations.

## Dependencies and Integration Points

- Generated metadata: field order, descriptor order, slot constants, and struct fields must stay aligned with `dist/stat.py` output and `src/include/stat.h`.
- Internal WiredTiger headers: `stat.c` includes `wt_internal.h`, which brings in `WT_CONNECTION_STATS`, `WT_SESSION_STATS`, `WT_CURSOR_STAT`, `WT_UNUSED`, and statistic helper declarations/macros.
- Statistics cursors: descriptor helpers are used by cursor-stat code to translate stat slots into stable text descriptions for application-visible statistics cursors.
- Runtime subsystems: the fields aggregated here are written by capacity, checkpoint, cache/eviction, cursor, data-handle, disaggregated storage, live restore, lock, log, prefetch, reconciliation, session, tiered, and transaction code paths.
- Thread-safety behavior: `WT_STAT_CONN_READ` routes through the aggregate helper and the statistic infrastructure's current synchronization strategy. This chunk relies on that layer for any concurrent-read handling.
- Language bindings and tests: public stat constants are exposed to language bindings, including Python's `wiredtiger.stat.conn` and `wiredtiger.stat.session`, so descriptor and struct order changes can affect external tests and applications.

## Risks and Maintenance Notes

- Generated drift is the main risk. A field added to `WT_CONNECTION_STATS` or `WT_SESSION_STATS` must be reflected in generated descriptor arrays, clear logic, and aggregation logic. Hand edits to this file would be overwritten or could break slot alignment.
- `__wt_stat_session_desc` does not bounds-check `slot`; callers must provide a valid generated session-stat slot index. A bad slot would index outside `__stats_session_desc`.
- The additive connection aggregation means stale destination data can double-count if the destination was expected to start at zero but was not cleared by the caller.
- Some fields look like gauges or current state values rather than monotonically increasing counters, for example active thread counts, live restore state, load values, checkpoint state, timestamp values, and local object in-use counts. This function still adds them using the generated connection aggregation convention; callers and stat definitions must agree on whether a field is meaningfully aggregatable across slots/sources.
- Session clear intentionally preserves transaction dirty-byte/update counters. Tests or callers expecting a full reset must use initialization or explicitly handle transaction fields.
- The broad set of stat families in this range makes omission bugs easy when generated sources change; compile success alone is not enough to prove public statistic ordering and descriptions are correct.

## Test Signals

Useful validation signals for this chunk include:

- Generated-file checks that rerun `dist/stat.py` and verify `src/support/stat.c` and `src/include/stat.h` are unchanged.
- Statistics cursor tests that open connection and session statistics cursors and confirm slot IDs, descriptions, and values line up with `WT_STAT_CONN_*` and `WT_STAT_SESSION_*` constants.
- Reset tests for session statistics that verify `bytes_read`, `bytes_write`, lock waits, read/write time, and cache wait counters clear, while `txn_bytes_dirty` and `txn_updates` survive `__wt_stat_session_clear_single`.
- Aggregation tests that populate multiple connection statistic slots and check that `__wt_stat_connection_aggregate` returns summed values for representative fields from this chunk, including capacity, checkpoint, cursor, log, reconciliation, tiered, and transaction families.
- Concurrency-oriented statistic tests or sanitizer runs that exercise concurrent statistic updates while connection stats are read, since this code depends on `WT_STAT_CONN_READ` and lower-level statistic helpers for safe aggregate reads.
