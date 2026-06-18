# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable.py

## Purpose
Implements persistent immutable share files and the bucket writer/reader objects used by Foolscap and HTTP storage protocols.

## Important APIs, Types, and Functions
Defines `_fix_lease_count_format()`, `ShareFile`, `BucketWriter`, `FoolscapBucketWriter`, `BucketReader`, and `FoolscapBucketReader`. `ShareFile` handles on-disk data and lease records. `BucketWriter` manages in-progress upload ranges, conflicts, timeouts, final rename, and abort. `BucketReader` reads committed share bytes and reports corruption.

## Control Flow
Creating a `ShareFile` writes a schema header and later appends leases after the maximum data area. Opening an existing file reads version, lease count, schema, data length, and lease offset. `BucketWriter.write()` resets a 30-minute timeout, checks overlapping writes for byte equality, writes data, updates a `RangeMap`, records server latency/counts, and returns completion. `close()` renames incoming to final location and cleans empty incoming dirs. `abort()` removes incoming state and notifies the storage server.

## State and Persistence Behavior
Immutable share files persist as `version`, capped data length, lease count, share data, and fixed-size lease records. Uploads are staged under incoming paths, then atomically renamed to final share paths on close. Lease add/renew/cancel mutates records in place; cancelling the last lease unlinks the share. `BucketWriter` tracks required ranges in memory.

## Dependencies and Integration Points
Depends on versioned schemas from `immutable_schema`, lease serializers, `RangeMap`, Foolscap `Referenceable`, Tahoe storage interfaces, `fileutil`, logging, and `StorageServer` callbacks/counters. HTTP server tracks `BucketWriter` instances directly; Foolscap wrappers expose remote methods.

## Risks and Edge Cases
Crashes during lease compaction could leave partially rewritten lease records, though ordering tries not to lose non-cancelled leases. `close()` cannot assert completion for backward compatibility with old Foolscap clients. Timeout/abort cleanup must avoid deleting non-empty shared incoming dirs. Lease count format is test-configurable and can overflow.

## Test Signals
`test_storage.py` covers share create/read/write, bounds, overlapping writes, required ranges, timeouts, close/abort cleanup, bad versions, lease renewal/cancel/overflow, immutable length, server allocation, and Foolscap bucket wrappers. HTTP tests add upload/read/conflict coverage through the new transport.
