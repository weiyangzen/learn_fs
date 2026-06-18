# sources/object-store/rustfs/crates/ecstore/src/bucket/quota/checker.rs

Purpose: Enforces bucket quota checks around object operations and persists quota config changes through bucket metadata.

Important APIs and types: `QuotaChecker` owns an `Arc<RwLock<BucketMetadataSys>>`. `check_quota` delegates to `check_quota_with_usage_reporting`. `get_quota_config` reads raw quota JSON from metadata, returning an unlimited default when absent. `set_quota_config` serializes `BucketQuota` and calls metadata `update`. `get_quota_stats`, `bucket_exists`, and `get_real_time_usage` support API reporting.

Control flow and state: If no quota is configured, operations are allowed and usage calculation is skipped unless forced. With a quota, current usage is read from `get_bucket_usage_memory`; PUT/POST/COPY add operation size and may be rejected, while DELETE is always allowed and subtracts with saturation for remaining reporting. Quota sync/check metrics are recorded through `rustfs_common::metrics`.

Dependencies and integration: Depends on `metadata_sys`, `data_usage::get_bucket_usage_memory`, `rustfs_config::QUOTA_CONFIG_FILE`, quota DTOs/errors from `quota/mod.rs`, and metrics.

Risks: Usage comes from memory and defaults to zero on missing/error in `get_real_time_usage`, which can under-enforce quota if the usage cache is cold or unavailable. Concurrent writers can race between usage check and object write. `current_usage + operation_size` is not saturating for expected PUT/COPY usage and could overflow in extreme values.

Test signals: Unit tests cover simple quota DTO allowance calculations and no-limit result shape. They do not instantiate a fake metadata system or test usage-cache failures/concurrency.
