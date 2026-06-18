# sources/storage-engines/wiredtiger/src/session/session_api.c

## Purpose
Defines most of the public `WT_SESSION` API vtable and its internal helpers: session open/close/reset/reconfigure, cursor open/cache behavior, schema APIs, logging APIs, transaction APIs, checkpointing, truncate, error inspection, and read-only/minimal-mode method tables.

## Important APIs, Types, and Functions
- `__open_session`, `__wt_open_session`, and `__wt_open_internal_session` allocate and initialize session slots, method tables, cursors, dhandle caches, transaction state, hazard arrays, statistics buckets, event handlers, and error buffers.
- `__wt_session_close_internal`, `__session_close_cursors`, and `__session_clear` unwind transactions, cursors, cached handles, metadata tracking, hazard pointers, resources, and session-array state.
- `__session_open_cursor_int`, `__wt_open_cursor`, and `__session_open_cursor` route cursor URIs to table/file/index/config/log/layered/backup/statistics/version/extension cursor implementations and integrate cursor caching.
- Schema-facing APIs include `create`, `alter`, `drop`, `publish`, `salvage`, `truncate`, `verify`, `compact` vtable binding, and checkpoint.
- Transaction APIs wrap begin, commit, prepare, rollback, timestamp/prepared-id setters, query timestamp, reset snapshot, and pinned range.
- `__wt_session_range_truncate` normalizes URI/cursor truncate requests and builds `WT_TRUNCATE_INFO` for schema/btree/table truncate layers.

## Control Flow
All public methods enter through `SESSION_API_*` macros that enforce connection/session state, configuration parsing, transaction/prepared checks, and error mapping. Cursor open first validates connection readiness and URI/duplicate arguments, tries the cursor cache, dispatches by URI prefix or data source, duplicates positions when needed, and records timing stats in diagnostic builds. Schema methods validate names and take schema/table/checkpoint locks in operation-specific combinations. Transaction methods check context, update counters, call transaction core functions, and handle rollback or panic rules for failed prepared commits/rollbacks.

Session close disables cursor caching, rolls back active transactions, releases snapshots, closes active and cached cursors, closes cached dhandles, destroys hazard and metadata state, releases common resources, updates session counters under the API lock, then carefully clears only the safe prefix of the reusable session object. Session open chooses normal, minimal, or read-only method tables, initializes queues and hash tables, transaction state, flags, prefetch defaults, config, error state, and finally publishes `active` with a release barrier.

## State and Persistence Behavior
This file is a central state coordinator. It maintains session active state, cursor lists/cache buckets, dhandle cache arrays, transaction state, hazard arrays, scratch/error buffers, stats, operation tracking buffers, prefetch flags, and per-session API method pointers. It drives durable behavior through transaction commit/rollback/prepare, checkpoint, log flush/printf, schema metadata updates, salvage, truncate logging, and checkpoint-created snapshots. `__wt_session_range_truncate` preserves original keys for write-ahead truncate logging even when the resolved range is empty.

## Dependencies and Integration Points
Highly integrated with transaction, cursor, schema, checkpoint, logging, statistics, event handler, dhandle, hazard, metadata tracking, prefetch, call-log, and connection lifecycle subsystems. It calls into `schema_truncate.c`, `schema_worker.c`, `session_compact.c`, `session_dhandle.c`, `session_helper.c`, and many cursor implementations.

## Risks
The largest risks are lock-order regressions, session reuse races, cursor-cache stale-handle retention, incorrect transaction error handling, prepared-transaction panic semantics, and URI dispatch drift as new object types are added. Session close/open barriers protect hazard/session-array users; clearing too much or publishing active too early can create use-after-free or uninitialized-read bugs. Truncate has high correctness risk because it moves application cursors, logs original bounds, handles empty ranges, and maps prepare conflicts to rollback.

## Test Signals
Relevant signals include API contract tests for each `WT_SESSION` method, read-only and minimal connection tests, cursor cache reuse/sweep tests, duplicate cursor tests, backup cursor duplication, truncate range and empty-range recovery tests, transaction prepare/commit/rollback error tests, checkpoint-in-transaction rejection, session open/close stress, hazard/session-array race tests, and diagnostic timing/stat counter assertions.
