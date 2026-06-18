# sources/object-store/garage/src/model/s3/block_ref_table.rs

## Purpose
This file defines the block-reference metadata table connecting stored data blocks to object versions. It drives block manager refcounts when references are created or deleted.

## Important APIs, types, and functions
`BlockRef` stores block hash, version UUID, and CRDT bool deletion state. It implements `Entry<Hash, Uuid>`, `is_tombstone`, and CRDT merge. `BlockRefTable` holds a `BlockManager` and implements `updated` to call `block_incref` or `block_decref`. `block_ref_recount_fn` returns a `CalculateRefcount` closure. `calculate_refcount` scans table rows for a block and counts non-deleted refs.

## Control flow
When a block ref transitions from deleted/absent to live, `updated` increments the block manager refcount in the same DB transaction. When it transitions from live to deleted/absent, it decrements. Version deletion cascades enqueue deleted `BlockRef` records from `version_table.rs`.

## State and persistence behavior
Rows are sharded by block hash and sorted by version UUID. Deletion is a CRDT bool tombstone. Refcount changes affect block manager persistent/local state via transaction hooks. Recount can recompute expected refcount from table contents for repair.

## Dependencies and integration points
It depends on Garage DB, table replication/schema traits, `BlockManager`, `CalculateRefcount`, and version table deletion cascades. `Garage::new` registers recount closure with the block manager.

## Risks and edge cases
If table hook errors are ignored upstream or a repair is needed, block refcounts can diverge from metadata. `calculate_refcount` assumes table keys for one hash are contiguous and decodable. Deleting a version with duplicate block hashes still creates per-version refs, so refcount semantics are per live version reference.

## Test signals
No direct tests. Good tests should cover incref/decref transitions, CRDT deletion merges, recount scanning, and version-delete cascade integration.
