# sources/storage-engines/wiredtiger/src/schema/schema_worker.c

## Purpose
Implements generic schema traversal for operations that must apply to all physical handles backing a logical object, such as verify, salvage, checkpoint handle collection, backup, and compaction. It expands table, column-group, index, tiered, and layered URIs into underlying file or data-source operations.

## Important APIs, Types, and Functions
- `__wt_schema_worker(session, uri, file_func, name_func, cfg, open_flags)` is the main recursive dispatcher.
- `__wti_execute_handle_operation` optionally closes existing handles for exclusive operations, opens a btree checkpoint/dhandle, invokes `file_func`, and releases the dhandle.
- `__schema_tiered_worker` iterates tiers in a `WT_TIERED` handle.
- `__schema_layered_worker_verify` verifies layered stable and ingest constituents with leader/follower-specific semantics.
- `name_func` callbacks can inspect intermediate URIs and request skips; `file_func` executes against opened btree handles.

## Control Flow
The worker first gives `name_func` a chance to skip the requested URI. It rejects verify/salvage for tiered objects. It then routes: files execute directly; colgroups and indexes resolve to sources; tables open table metadata, visit all colgroups and optionally indexes; layered verify delegates to stable/ingest checks; tiered walks each tier; extension data sources use salvage/verify hooks when available. Checkpoint-related file functions are no-ops for unsupported extension sources.

## State and Persistence Behavior
This file coordinates handle state rather than writing metadata itself. Exclusive operations may close open handles before re-opening the target. Layered verification reads stable and ingest constituents, and leader ingest verification requires the ingest table to be empty. Recursive traversal must release opened table metadata on all exits.

## Dependencies and Integration Points
Used by session APIs for salvage and verify, by compaction handle gathering, checkpoint handle paths, backup-style traversals, and schema code that needs source-tree expansion. It depends on table/index/colgroup metadata APIs, dhandle open/release, layered/tiered handle types, data-source extension hooks, and `__wt_verify`, `__wt_salvage`, and checkpoint callbacks.

## Risks
Recursive traversal can miss physical files if table/index metadata is not opened under the right table lock. Operations differ in whether they need indexes opened, and this file keys that on `WT_SESSION_LOCKED_TABLE_WRITE`. Verify/salvage tiered restrictions must remain consistent with feature support. Layered follower handling intentionally ignores transient missing stable tables, which needs focused testing to avoid hiding real corruption.

## Test Signals
Coverage should include verify/salvage for files, tables, indexes, colgroups, tiered rejection, layered leader/follower verify, name callback skip behavior, exclusive-handle close behavior, and checkpoint/backup traversal paths that depend on index opening under table write lock.
