# sources/object-store/garage/src/table/schema.rs

Purpose: generic schema traits for Garage replicated tables.

Important APIs and types: `PartitionKey` hashes a partition key to `Hash`; implemented for `String` via Blake2 and `FixedBytes32` as identity. `SortKey` exposes sortable bytes; implemented for `String` and `FixedBytes32`. `Entry<P, S>` requires CRDT merge, equality, clone, migration support, and key accessors, with optional `is_tombstone`. `TableSchema` defines table name, key types, entry type, filter type, schema-level `updated` hook, and `matches_filter`.

Control flow: table reads build DB keys from partition hash plus sort key and apply `matches_filter` during scans. Mutations call `Entry::merge` for CRDT updates and invoke `TableSchema::updated` inside the same DB transaction as the table update, allowing secondary local DB changes to remain atomic.

State and persistence: trait implementors define the serialized entries stored by `TableData`. Migration support lets decoded entries be normalized on rewrite.

Dependencies and integration: central contract for all Garage table definitions, `TableData`, queue, sync, GC, and public table API. Uses `garage_db::Transaction` for hooks.

Risks and test signals: schema implementors must make `partition_key`/`sort_key` stable and ensure CRDT/tombstone semantics are correct. A bad `updated` hook can abort mutations or break secondary indexes. No direct tests in this file; each table schema should test its own behavior.
