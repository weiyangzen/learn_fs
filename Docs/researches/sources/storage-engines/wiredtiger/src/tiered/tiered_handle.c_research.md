# sources/storage-engines/wiredtiger/src/tiered/tiered_handle.c Research

## Purpose
This file owns tiered table handle lifecycle and object switching. It creates and opens tiered data handles, generates local/shared/object names, manages tier arrays and dhandle references, writes tiered metadata, detects stale shared objects on create, and schedules tiered work when switching objects or restarting after a crash.

## Important APIs, Types, and Functions
- Name and existence helpers: `__tiered_name_check`, `__tiered_name_str`, and public `__wt_tiered_name`.
- Dhandle setup helpers: `__tiered_dhandle_setup`, `__tiered_init_tiers`, `__tiered_update_dhandles`, and `__tiered_cleanup_tiers`.
- Object and metadata creation: `__tiered_create_local`, `__tiered_create_object`, `__tiered_create_tier_tree`, `__wt_tiered_set_metadata`, and `__tiered_update_metadata`.
- Switching and restart: `__tiered_restart_work`, internal `__tiered_switch`, and public `__wt_tiered_switch`.
- Lifecycle APIs: `__wt_tiered_open`, `__wt_tiered_close`, `__wt_tiered_discard`, `__wt_tiered_tree_open`, and `__wt_tiered_tree_close`.

## Control Flow and State
Open starts by resolving bucket storage from table or connection config, merging config for later metadata updates, and constructing object config with `readonly=true,tiered_object=true`. It reads key/value formats, `last`, `oldest`, and `tiers`. Existing tiered handles initialize dhandles from the tiers list and may switch during import. New handles first check shared storage for old objects with the same logical table name, then switch to create initial local metadata.

Switching runs under metadata tracking and is documented as single-threaded. It decides whether an `object:` metadata entry and `tier:` shared tree are needed from the existing local/shared tier state. It optionally requeues restart work for unflushed earlier objects on first flush after restart. It creates object metadata for the current local object, queues a flush work unit, creates the next local `file:` object, updates the `tiered:` metadata with `flush_time`, `flush_timestamp`, `last`, `oldest`, and `tiers`, commits metadata tracking, then refreshes dhandle references.

## State and Persistence Behavior
This is a persistent metadata module. It creates and updates `tiered:`, `file:`, `object:`, and `tier:` metadata entries and uses metadata tracking so multi-step switch operations commit or roll back together. It stores object ids in `current_id`, `next_id`, and `oldest_id`, and records tier names plus operation flags in the tier array. It also writes flush metadata from the active btree's `flush_most_recent_secs` and `flush_most_recent_ts`.

## Dependencies and Integration Points
The file depends on schema create/update, metadata cursor/search/insert, import metadata, btree open/close/discard, dhandle acquisition/release, tiered work queue functions, storage-source file-system directory listing, timestamp hex formatting, and config merge/collapse utilities. It bridges connection/table configuration from `tiered_config.c` with asynchronous work in `tiered_work.c`.

## Risks and Edge Cases
Object switching is complex and must remain single-threaded. A crash between metadata steps is handled by metadata tracking and restart work scanning, but ordering bugs can leave local objects unflushed or dhandles stale. `__tiered_name_check` uses prefix and fixed-length object naming to avoid false positives from superset names; changes to name format must preserve that assumption. Dhandle reference counts are manually incremented/decremented, so missed cleanup risks handle leaks or premature sweep. Import paths insert metadata for objects that may or may not exist and tolerate missing old objects. The code still has temporary `#if 1` dead code to satisfy style checks, suggesting some shared-remove paths are not fully wired.

## Test Signals
Tests should cover creating a new tiered table, reopening existing local/shared states for all documented `tiers` combinations, object switch metadata atomicity, import switching, stale shared-object create rejection, crash/restart with unflushed local objects, dhandle reference cleanup on open failure, correct name generation for local/object/shared/prefix/name-only modes, and retention/flush work queue scheduling after switch.
