# sources/object-store/garage/src/model/s3/mpu_table.rs

## Purpose
This file defines metadata for active and deleted multipart uploads. It tracks uploaded part versions, propagates cleanup to version metadata, and contributes per-bucket MPU counters.

## Important APIs, types, and functions
`MultipartUpload` stores upload UUID, creation timestamp, CRDT deleted flag, CRDT map of `MpuPartKey` to `MpuPart`, and backlink bucket/key. `MpuPartKey` orders by part number then timestamp. `MpuPart` stores version UUID, optional ETag, optional checksum, and optional size. `MultipartUpload::new` and `next_timestamp` are constructors/helpers. `MultipartUploadTable::updated` updates counters and propagates deletions to `VersionTable`. `CountedItem` metrics are `UPLOADS`, `PARTS`, and `BYTES`.

## Control flow
Retries for the same part get unique timestamps and all versions remain until upload deletion. CRDT merge marks deletion dominant: once deleted, parts are cleared. Part merge chooses present/max ETag, size, and checksum values. When an MPU transitions from live to deleted, table update code queues deletion `Version` entries for all previously known part versions.

## State and persistence behavior
The current initial format marker is `G09s3mpu`. Rows are keyed by upload UUID. Deleted rows are tombstones. Counters aggregate active upload count, distinct part numbers, and known part sizes by bucket. Version cleanup is queued transactionally but hook failures are logged and require repair.

## Dependencies and integration points
It depends on object-table checksum types, version table, index counters, Garage DB, and sharded table replication. S3 multipart API paths create/update/delete these rows; object-table completion/abortion also deletes MPU rows.

## Risks and edge cases
`counts` deduplicates part numbers by calling `dedup` without sorting the collected numbers; because `parts.items()` is ordered by `MpuPartKey`, equal part numbers should be adjacent, but that invariant matters. Deletion clears parts after merge, so late part updates lose to deletion. Hook failures can leave orphaned versions. Optional size/checksum fields mean counters may undercount bytes for in-progress parts.

## Test signals
No direct tests in this file. Multipart integration tests should exercise it. Focused tests should cover part ordering, retry timestamps, deletion cascades, counter metrics, and merge dominance of deletion.
