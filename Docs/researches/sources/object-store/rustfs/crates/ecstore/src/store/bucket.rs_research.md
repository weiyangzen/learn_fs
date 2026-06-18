# sources/object-store/rustfs/crates/ecstore/src/store/bucket.rs

## Purpose
Implements top-level bucket operations for `ECStore`: create, stat, list, and delete buckets, including metadata persistence, object-lock/versioning initialization, table-bucket delete guards, and cleanup of internal bucket metadata.

## Important APIs, Types, And Functions
Helpers include `should_override_created_from_metadata`, `validate_table_bucket_delete_allowed`, `table_catalog_metadata_exists`, `validate_table_bucket_delete_guard`, and `bucket_delete_metadata_cleanup_prefixes`. Handler methods are `handle_make_bucket`, `handle_get_bucket_info`, `handle_list_bucket`, and `handle_delete_bucket`.

## Control Flow
`handle_make_bucket` validates names, optionally takes a namespace write lock, asks peers to create the bucket, tries best-effort bucket heal on `BucketExists`, rolls back peer-created state on non-exists errors, creates `BucketMetadata`, initializes object-lock/versioning XML if requested, saves metadata, and updates the metadata system. Delete validates names, takes a lock, verifies bucket existence, enforces table-bucket catalog guard, recursively scans local disks for `xl.meta` unless forced, calls peer delete, deletes internal metadata prefixes, and updates the bucket monitor.

## State And Persistence Behavior
Persists bucket metadata via `BucketMetadata::save` and `set_bucket_metadata`. Delete removes bucket data through peers and cleans `RUSTFS_META_BUCKET` prefixes for table catalog and bucket metadata. Empty-directory remnants do not count as objects; only `xl.meta` files do.

## Dependencies And Integration Points
Depends on peer system bucket operations, namespace locks, bucket metadata system, object-lock/versioning serializers, local disk enumeration, `has_xlmeta_files`, table-bucket metadata conventions, and the global bucket monitor.

## Risks
Local recursive emptiness scans can be expensive and only see local disks. `delete_all` cleanup is best effort and may hide per-disk metadata deletion failures. Bucket creation rollback after peer failure is also best effort. Table-bucket guards depend on metadata state being available and accurate.

## Test Signals
Tests cover created-time override rules, table-bucket delete guard behavior, and metadata cleanup prefixes including table catalog metadata. Additional integration tests should cover lock errors, peer rollback, force delete, and object-lock/versioning metadata serialization.
