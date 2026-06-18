# sources/object-store/rustfs/crates/scanner/tests/lifecycle_integration_test.rs

## Purpose
This is an integration test suite for RustFS scanner lifecycle behavior over a local four-disk `ECStore`. It exercises zero-day lifecycle expiry, current and noncurrent version transitions, delete marker cleanup, free-version cleanup, and restore from a transitioned warm tier. Most tests are serial and many are ignored because they depend on isolated global object-layer state or long-running scanner timing.

## Important APIs, Types, and Helpers
The setup helpers construct either a cached global test store (`setup_test_env`) or a fresh store (`setup_isolated_test_env`) by creating four `/tmp/rustfs_scanner_lifecycle_test_*` disk directories, converting them to `Endpoint`s, calling `init_local_disks`, building an `ECStore`, initializing bucket metadata, and optionally starting background expiry workers.

Bucket and object helpers wrap store operations: `create_test_bucket`, `create_test_lock_bucket`, `upload_test_object`, and `modeled_versioned_delete_opts`. Lifecycle helpers write XML directly to `metadata_sys::update` under `BUCKET_LIFECYCLE_CONFIG`: current expiry, expired-object-delete-marker cleanup, `DelMarkerExpiration`, transition rules, and transition rules with an arbitrary tier.

Scanner helpers open a single local disk with `new_disk`, locate the object `xl.meta` path (`STORAGE_FORMAT_FILE`), build a `ScannerItem`, and call `ScannerIODisk::get_size` with or without lifecycle metadata. Poll helpers observe object absence, remote-tier object counts, object version counts, and completed transition state. `MockWarmBackend` implements `WarmBackend` in memory and preserves bytes plus selected metadata derived through `build_transition_put_options`.

## Control Flow and State
Tests create buckets, install lifecycle XML, mutate object state through `put_object`, multipart upload, `copy_object`, `delete_object`, or `restore_transitioned_object`, then trigger either `enqueue_transition_for_existing_objects`, `init_background_expiry`, manual scanner `get_size`, or `init_data_scanner`. Assertions poll with short timeouts to account for async lifecycle workers.

The file uses global state in several places: `GLOBAL_ENV` caches one `ECStore`; `GLOBAL_TierConfigMgr` is mutated to register test tiers and mock drivers; and `with_forced_immediate_enqueue_timeout` mutates `ENV_TEST_FORCE_IMMEDIATE_TRANSITION_ENQUEUE_TIMEOUT` under `#[serial]` tests. Persistent state is filesystem metadata on the temporary disks and in-memory warm-tier maps.

## Integration Points
The suite crosses `rustfs_ecstore`, `rustfs_scanner`, `rustfs_filemeta`, `rustfs_storage_api`, `rustfs_config`, and `s3s` restore DTOs. It verifies integration between bucket metadata lifecycle config, object versioning, erasure-store metadata, scanner item traversal, background expiry queues, warm-tier transition drivers, multipart restore, and object-lock/versioning options.

## Risks
The tests are timing-sensitive and rely on background async workers, process environment mutation, and global tier registry state. One ignored test sleeps for 1200 seconds, which is unsuitable for normal CI. Manual single-disk scanner calls may not exercise all erasure-set behavior. Because many important scenarios are ignored, regressions can pass default test runs unless the ignored integration suite is run in a controlled environment.

## Test Signals
Covered scenarios include immediate transition for normal put, multipart upload, copy, existing-object backfill, restore of transitioned multipart objects, stale free-version remote cleanup, idempotent backfill after compensation transition, noncurrent expiry/transition after compensation, modeled versioned delete marker creation and cleanup, immediate zero-day current and noncurrent expiry on put, scanner-driven zero-day expiry, and background scanner expiry for prefix and exact-key rules.
