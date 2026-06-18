# sources/object-store/garage/src/model/helper/bucket.rs

## Purpose
This file provides bucket lookup and cleanup helpers around `Garage`. It separates fast local reads used by request hot paths from quorum reads used by admin/control operations, and implements bucket emptiness checks plus incomplete upload cleanup.

## Important APIs, types, and functions
`BucketHelper` wraps `&Garage`. `resolve_global_bucket_fast` and `resolve_bucket_fast` use local table copies. `resolve_global_bucket` and `resolve_bucket` perform quorum table reads. `get_internal_bucket` retrieves a bucket even if deleted; `get_existing_bucket` requires a present bucket. `is_bucket_empty` scans S3 data objects and optional K2V counters. `cleanup_incomplete_uploads` aborts stale uploading object versions.

## Control flow
Bucket names can be a global alias, local key alias, or full hex UUID. Fast functions decode 64-character UUIDs or consult local alias/key state, then local bucket state. Quorum versions use table `get` calls, fetching the key table before interpreting local aliases. Cleanup pages through `object_table` ranges with `ObjectFilter::IsUploading`, creates `ObjectVersionState::Aborted` entries for versions older than the threshold, and inserts those object updates in batches.

## State and persistence behavior
Lookup helpers are read-only. `cleanup_incomplete_uploads` persists object updates that cause `ObjectTable::updated` to cascade version/MPU cleanup through table hooks. `is_bucket_empty` is read-only but uses counters for K2V when enabled, filtering to current non-gateway nodes from cluster layout.

## Dependencies and integration points
The helper depends on bucket, alias, key, object-table, K2V counter, table utility, layout, and time modules. S3 API handlers use fast lookup for normal requests; admin operations use quorum lookup. Lifecycle and bucket-delete paths rely on cleanup/emptiness checks.

## Risks and edge cases
Fast helpers intentionally do not provide read-after-write guarantees. A bucket name that decodes as a 32-byte UUID bypasses alias lookup. `cleanup_incomplete_uploads` computes `now_msec() - older_than`, so a duration larger than current epoch milliseconds would underflow. K2V emptiness depends on counter correctness, which can lag if counter update hooks failed.

## Test signals
No direct tests are present. Valuable coverage includes UUID-vs-alias resolution, stale local alias behavior, quorum read behavior after mutations, cleanup pagination, abort cascades, and K2V counter-based emptiness.
