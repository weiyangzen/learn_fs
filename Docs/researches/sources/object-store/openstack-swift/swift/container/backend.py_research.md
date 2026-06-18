# sources/object-store/openstack-swift/swift/container/backend.py

## Purpose
This module implements Swift's SQLite-backed container database broker. It owns object listing rows, per-storage-policy stats, container metadata/status, shard range persistence, schema migrations, sharding state transitions, misplaced-object discovery, and listing/query behavior. It is the persistence core for container servers and sharding machinery.

## Important APIs, Types, and Functions
- Constants define container DB location and schema semantics: `DATADIR`, record types, shard states (`UNSHARDED`, `SHARDING`, `SHARDED`, `COLLAPSED`), shard state groups, `SHARD_RANGE_KEYS`, and SQL scripts for `policy_stat`, `container_info`, `container_stat`, and triggers.
- `update_new_item_from_existing()` merges incoming object rows against existing rows using data, content-type, and metadata timestamps encoded in `created_at`.
- `merge_shards()` and `sift_shard_ranges()` apply shard-range precedence rules for creation timestamp, metadata timestamp, state timestamp, deleted flag, epoch, reported latch, and tombstone count.
- `ContainerBroker(DatabaseBroker)` is the primary API for container DB creation, querying, updates, replication info, migrations, sharding, root/shard metadata, and shard-range discovery.
- Creation and schema APIs include `create_broker()`, `_initialize()`, `create_object_table()`, `create_policy_stat_table()`, `create_container_info_table()`, and `create_shard_range_table()`.
- Object APIs include `put_object()`, `delete_object()`, `merge_items()`, `remove_objects()`, `list_objects_iter()`, `get_objects()`, `_transform_record()`, and `_record_to_dict()`.
- Info/stat APIs include `get_info()`, `_get_info()`, `_get_alternate_object_stats()`, `get_policy_stats()`, `set_storage_policy_index()`, `reported()`, `empty()`, and reclaim helpers.
- Reconciler APIs include `get_reconciler_sync()`, `update_reconciler_sync()`, and `get_misplaced_since()`.
- Shard APIs include `merge_shard_ranges()`, `get_namespaces()`, `get_shard_ranges()`, `get_own_shard_range()`, `enable_sharding()`, `set_sharding_state()`, `set_sharded_state()`, `get_brokers()`, root metadata properties, and `find_shard_ranges()`.

## Control Flow and Behavior
`ContainerBroker` may represent more than one on-disk DB file during sharding. `_init_db_file` is the legacy path, `db_files` discovers valid files by epoch, `db_file` selects the authoritative newest file unless forced, and `get_brokers()` returns both retiring and fresh brokers during `SHARDING`. State is inferred from file count, filename epoch, own shard range epoch, and presence of other shard ranges.

Object writes flow through `put_record()` inherited from `DatabaseBroker` and later `merge_items()`. `merge_items()` begins an immediate SQLite transaction, fetches existing rows by name in chunks under SQLite argument limits, applies `update_new_item_from_existing()`, deletes superseded rows, inserts new rows, and updates incoming replication sync points. SQL triggers update `policy_stat` counters on insert/delete while prohibiting `UPDATE` of object rows.

Listings in `list_objects_iter()` commit pending puts first, build SQL predicates for markers, end markers, prefix, delimiter, path, reverse order, deletion mode, policy selection, reserved-byte filtering, and row-id bounds. Delimiter handling may iterate and requery to produce pseudo-directory entries while respecting limit.

Shard-range persistence mirrors object merge behavior but uses `merge_shards()` precedence. Query APIs convert rows into `ShardRange` or `Namespace` objects, sort with Swift shard sort keys outside SQLite because the maximum upper bound is represented by an empty string, and optionally fill a trailing gap with a modified own shard range.

Schema compatibility is active and lazy. Missing `storage_policy_index`, `policy_stat`, sync point, shard `reported`, shard `tombstones`, or `shard_range` table errors trigger migrations or compatibility defaults. Legacy `container_stat` is replaced by a view backed by `container_info` and `policy_stat`, with triggers preserving old update behavior.

Sharding state transition in `set_sharding_state()` creates a fresh epoch DB, copies metadata, shard ranges, and sync points, initializes object ROWID continuity with a temporary row, syncs selected container status fields, then atomically renames the fresh DB into place. `set_sharded_state()` unlinks the retiring DB only when a fresher DB is present.

## State and Persistence
Persistence is SQLite files under the container data directory plus `.pending` files inherited from `DatabaseBroker`. Core tables are `object`, `policy_stat`, `container_info`, compatibility view `container_stat`, sync tables from the base broker, and `shard_range`. Triggers maintain object counts, bytes, hashes, and policy stats. Metadata includes sharding sysmeta keys such as `X-Container-Sysmeta-Shard-Root` and quoted root. Cached in-memory state includes db file lists, storage policy index, account/container identity, root account/container, and database version.

## Dependencies and Integration Points
The broker extends `swift.common.db.DatabaseBroker` and uses Swift timestamp encoding, sharding types (`ShardRange`, `ShardRangeList`, `Namespace`), path hashing/storage helpers, DB filename epoch helpers, `tpool` for blocking SQLite merge work, and container listing limits. It integrates with container server request handling, replicator, updater, sharder, reconciler, auditor, and account/stat reporting paths.

## Risks and Edge Cases
- Timestamp merge semantics are subtle: data, content-type, metadata, and swift_bytes must be preserved independently despite sharing columns.
- Lazy migrations happen inside operational paths; migration failures can surface during reads or writes, not only at startup.
- Multi-DB sharding states require careful file selection and `skip_commits` behavior to avoid writing to retiring DBs incorrectly.
- `set_sharding_state()` manipulates ROWID continuity and file renames; partial failures before rename must not leave authoritative state ambiguous.
- Listing delimiter and reverse-marker logic is complex and prone to off-by-one or duplicate pseudo-directory bugs.
- Shard range sorting cannot rely on SQLite due to empty-string max bounds, so Python sort keys must remain consistent with sharding semantics.
- Root-container detection relies on sysmeta and own shard range deletion state, including legacy deleted shard cases.

## Test Signals
Important tests should cover object timestamp merges, swift_bytes extraction/restoration, policy-stat trigger counts, legacy schema migrations, pending put commits before reads, all listing combinations, replication sync updates, misplaced-object queries, shard-range merge precedence, namespace gap filling, DB state transitions, fresh epoch DB creation and retiring DB unlinking, root/shard metadata parsing, and reclaim safety for sharded containers.
