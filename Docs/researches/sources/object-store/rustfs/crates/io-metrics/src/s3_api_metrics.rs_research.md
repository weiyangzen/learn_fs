<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs

### Purpose
Records generic S3 API operation counts by operation and bucket and provides one-time metric description registration.

### Important APIs, Types, And Functions
`S3_OPS_METRIC` is `rustfs_s3_operations_total`. `record_s3_op` accepts `rustfs_s3_ops::S3Operation` and bucket name. `init_s3_metrics` uses `OnceLock<()>` to call `describe_counter!` only once.

### Control Flow
`record_s3_op` emits a counter labeled by `op.as_str()` and owned bucket string. `init_s3_metrics` lazily registers the counter description through `OnceLock::get_or_init`.

### State And Persistence
Only the `OnceLock` tracks whether the description was initialized in the current process. Metric counts are external to the module.

### Dependencies And Integration Points
Depends on `rustfs-s3-ops` for stable operation labels and on metrics macros imported at crate root. Re-exported from `lib.rs`.

### Risks
Bucket label cardinality can be very high in multi-tenant deployments. This may be acceptable for some observability backends but should be deliberate. There are no local tests in this file.

### Test Signals
No unit tests in the file. Compile coverage comes from crate build and any callers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/s3_api_metrics.rs -->
