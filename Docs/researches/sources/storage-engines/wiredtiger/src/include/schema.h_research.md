# sources/storage-engines/wiredtiger/src/include/schema.h

## Purpose
Declares schema-level data structures for column groups, indexes, tables, layered tables, truncate tracking, and import lists, plus lock helper macros that enforce schema/metadata/table/handle/backup lock order and re-entrant session lock tracking.

## Important APIs, Types, And Functions
- Projection characters: `WT_PROJ_KEY`, `WT_PROJ_NEXT`, `WT_PROJ_REUSE`, `WT_PROJ_SKIP`, and `WT_PROJ_VALUE`.
- `WT_COLGROUP`, `WT_INDEX`, `WT_TABLE`, `WT_TRUNCATE`, `WT_LAYERED_TABLE`, `WT_IMPORT_ENTRY`, and `WT_IMPORT_LIST` define schema object state.
- Flags include `WT_INDEX_IMMUTABLE`, `WT_LAYERED_TABLE_OPEN`, and `WT_IMPORT_INVALID_FILE_ID`.
- `WT_COLGROUPS` computes default/tiered-shared column group count.
- Lock-state masks combine handle-list, table, and hot-backup read/write flags.
- Generic lock macros `WT_WITH_LOCK_WAIT` and `WT_WITH_LOCK_NOWAIT` support re-entrant spinlocks using `session->lock_flags`.
- Specialized macros acquire checkpoint, handle-list read/write, metadata, schema, table read/write, and hot-backup read/write locks.

## Control Flow
Schema/table structures are passive state. Lock macros test session lock flags first to allow re-entrant use by the owning thread. Otherwise they acquire the correct spinlock or rwlock, set the session flag, execute caller-provided `op`, clear the flag, and unlock. Nowait variants surface `EBUSY` through `__wt_session_set_last_error`. Assertions enforce lock ordering, such as schema lock before handle-list/table locks and write locks not being taken while read locks are held.

## State And Persistence Behavior
Schema structures mirror persistent metadata entries for tables, column groups, indexes, layered table constituents, and imports. Truncate entries store transaction/timestamp visibility state and key ranges for layered table fast truncate. Lock flags are transient per-session state but protect persistent metadata and handle lifecycle updates.

## Dependencies And Integration Points
Depends on config items, data handles, collators, TAILQ, rwlocks/spinlocks, session lock flags, connection locks, backup state, session error reporting, and table/layered-table metadata. Integrated with schema create/drop/alter/open, import, tiered/layered tables, checkpoint, hot backup, and handle cache management.

## Risks
Lock macros execute arbitrary `op` inline; `op` must not bypass error handling or jump over unlock cleanup. Misordered locks can deadlock and are guarded mainly by assertions. Session lock flags assume a session is used by one thread at a time. Layered truncate state mixes lock-protected membership with lock-free committed visibility, so callers must honor the documented synchronization split.

## Test Signals
Schema tests should cover lock ordering assertions, nowait lock conflict error codes, re-entrant lock behavior, table/index/column-group open/close lifecycle, import sorting by file id including invalid ids, layered table truncate visibility, hot-backup read/write exclusion, and concurrent schema operations.
