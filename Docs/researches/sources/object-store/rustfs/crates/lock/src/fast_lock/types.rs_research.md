<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs

Purpose: `types.rs` defines the fast-lock public data model: object keys, lock modes, requests, results, configuration, lock info, and batch operation structures.

Important APIs/types/functions: `ObjectKey` stores bucket/object/version as `Arc<str>`, implements manual serde, ordering, display, latest/version constructors, and `shard_index`. `OptimizedObjectKey` uses `SmartString` and cached `OnceLock<u64>` hash with conversion to/from `ObjectKey`. `LockMode` is shared/exclusive. `ObjectLockRequest` has constructors for read/write and builders for version, acquire timeout, lock timeout, and priority. `LockPriority` defines Low/Normal/High/Critical. `LockResult` includes `Acquired`, `Timeout`, and `Conflict`. `LockConfig` supplies shard/default timeout/cleanup/metrics configuration. `ObjectLockInfo`, `BatchLockRequest`, and `BatchLockResult` model monitoring and batch acquisition outputs.

Control flow: these types are mostly passive. `ObjectKey::shard_index` hashes all key fields and masks by shard count. Request builders mutate and return `self`. Batch builder accumulates read/write requests using the batch owner and controls all-or-nothing behavior.

State and persistence behavior: keys and requests are cloneable in-memory values and serde-compatible where implemented. `ObjectKey` serde stores bucket, object, and optional version. `OptimizedObjectKey` hash cache is process-local and must be invalidated if fields are changed. `LockConfig::default` pulls constants from `fast_lock/mod.rs`; no values are persisted.

Dependencies and integration points: every fast-lock module depends on these types. `crate::types` defines a parallel higher-level lock model used by distributed/client APIs; `local_lock.rs` maps between the two priority and mode enums. `lib.rs` re-exports several fast-lock types publicly.

Risks: `LockResult::Acquired` is an odd error/result variant because successful acquisitions return `Ok(FastLockGuard)`; callers should rarely see it. `LockConfig::default_acquire_timeout` and `default_lock_timeout` are not applied by `ObjectLockRequest::new_*` through a manager config; request constructors use module constants directly. `BatchLockRequest::owner` is copied into new requests, but callers can also pass prebuilt requests with different owners if they construct the struct manually. `OptimizedObjectKey` is not currently the main map key in `LockShard`, so its benefits depend on future adoption.

Test signals: unit tests cover object key construction/display, request builders, and batch builder modes. Manager and namespace tests cover versioned-key behavior and batch requests indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/types.rs -->
