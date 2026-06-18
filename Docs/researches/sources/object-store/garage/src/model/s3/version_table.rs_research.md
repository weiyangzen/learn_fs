# sources/object-store/garage/src/model/s3/version_table.rs

## Purpose
This file defines metadata for the data blocks belonging to a single object or multipart part version. It provides the bridge from object/MPU metadata to block references and block refcount cleanup.

## Important APIs, types, and functions
`Version` stores UUID, CRDT deleted flag, CRDT map of `VersionBlockKey` to `VersionBlock`, and a `VersionBacklink` to either an object bucket/key or multipart upload ID. `VersionBlockKey` orders by part number then offset. `VersionBlock` stores block hash and uncompressed/plain size. `Version::new`, `has_part_number`, and `n_parts` are helpers. `VersionTable::updated` propagates deletion of block refs. v09 migrates from v08 by replacing bucket/key fields with `VersionBacklink::Object`.

## Control flow
When a version is marked deleted after previously being live, the update hook queues deleted `BlockRef` entries for every old block. Version merge makes deletion dominant and clears blocks if deleted; otherwise it merges block maps. `n_parts` reads the last block key's part number and errors if no blocks exist.

## State and persistence behavior
Current format marker is `G09s3v`; table name is `version`; rows are keyed by version UUID. Deleted rows are tombstones. Block maps are cleared after deletion, but the update hook uses the old live row to propagate block-ref tombstones.

## Dependencies and integration points
It depends on block-ref table, table replication, Garage DB, and error helpers. Object table and MPU table enqueue deleted versions; upload paths create live versions with blocks; block manager cleanup follows from block-ref table hooks.

## Risks and edge cases
If a delete update arrives without local old block data, block-ref deletion propagation may not happen from that node; repair/recount paths are needed. `has_part_number` uses binary search over ordered CRDT map items, relying on `VersionBlockKey` ordering. `n_parts` returns the highest part number, not necessarily a count of contiguous parts.

## Test signals
No direct tests. Useful coverage includes v08 migration, block ordering, delete cascade to block refs, `n_parts` empty/error behavior, and deletion merge dominance.
