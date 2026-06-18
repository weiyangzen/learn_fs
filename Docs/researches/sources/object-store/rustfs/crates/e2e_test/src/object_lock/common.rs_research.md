# sources/object-store/rustfs/crates/e2e_test/src/object_lock/common.rs

Purpose: shared Object Lock E2E helper layer. It centralizes server setup, Object Lock bucket creation, default retention configuration, object writes with retention or legal hold, retention/legal-hold mutations, delete operations with governance bypass, and future retention date calculation.

Important APIs/types/functions: `ObjectLockTestEnvironment` wraps `RustFSTestEnvironment` and exposes `new`, `start_rustfs`, `s3_client`, and `create_object_lock_bucket`. `put_object_lock_configuration` builds `DefaultRetention`, `ObjectLockRule`, and `ObjectLockConfiguration` for bucket defaults. `put_object_with_retention` maps `ObjectLockRetentionMode` to `ObjectLockMode`, formats UTC retain-until timestamps for the AWS SDK, and returns the created version id. `put_object_with_legal_hold`, `put_object_retention`, `put_object_legal_hold`, `delete_object_with_bypass`, and `future_retain_until` are reusable test operations.

Control flow: tests create an environment, start RustFS, create an Object Lock enabled bucket, then call these helpers to exercise S3 Object Lock APIs. Helpers construct SDK builders, optionally add version ids, send the requests, and log operation details. Date helpers deliberately format timestamps as `YYYY-MM-DDTHH:MM:SSZ` before parsing into AWS SDK `DateTime`.

State and persistence behavior: the helpers create real buckets and versioned objects in a temporary RustFS data directory. Object Lock enabled bucket creation is expected to trigger versioning behavior in the server. Returned version ids are the primary state handles used by the test suite for version-specific deletion, retention reads, and legal-hold reads.

Dependencies and integration points: uses `aws_sdk_s3` Object Lock model types, `ByteStream`, `chrono` for UTC date arithmetic, shared RustFS E2E environment, and `tracing`. It is imported by `object_lock_test.rs` as the common test DSL.

Risks: `retention_mode_to_lock_mode` falls back to governance for unknown strings, which is fine for tests using SDK enum values but would mask unexpected modes if reused more broadly. Date formatting truncates subsecond precision. Helpers return boxed dynamic errors, convenient for tests but not rich for diagnostics.

Test signals: this file is not itself a test module, but all Object Lock E2E test signals flow through it. Correctness is indirectly validated by delete, copy, multipart, retention mutation, default retention, and permission tests.
