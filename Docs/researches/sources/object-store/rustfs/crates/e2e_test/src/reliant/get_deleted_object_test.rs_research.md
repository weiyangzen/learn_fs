# sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs

Purpose: live-server regression tests for deleted or nonexistent object reads. The file documents a prior failure mode where `GetObject` on a deleted object surfaced as a networking error instead of a structured S3 `NoSuchKey`.

Important APIs and functions: `create_aws_s3_client` creates a path-style AWS SDK client for localhost RustFS. `setup_test_bucket` creates `test-get-deleted-bucket` and accepts both `BucketAlreadyExists` and `BucketAlreadyOwnedByYou`. Tests use `put_object`, `get_object`, `delete_object`, and `head_object`, then inspect `SdkError::ServiceError` and S3 error metadata.

Control flow: `test_get_deleted_object_returns_nosuchkey` uploads a key, verifies it can be fetched, deletes it, then asserts `get_object` returns a service error whose S3 error is `NoSuchKey`. `test_head_deleted_object_returns_nosuchkey` uploads and deletes, then accepts either `NoSuchKey` or `NotFound` for `HeadObject`. `test_get_nonexistent_object_returns_nosuchkey` calls `GetObject` for a never-created key. `test_multiple_gets_deleted_object` repeats the post-delete `GetObject` path five times to catch unstable state or race behavior.

State and persistence: object state lives in the local RustFS bucket. Tests use fixed keys in a fixed bucket, so serial execution and cleanup reduce interference but do not fully isolate between interrupted runs. Deletes are normal S3 deletes without explicit versioning.

Dependencies and integration points: AWS SDK S3 error classification, RustFS object deletion path, HTTP error serialization, `tracing` test logging, and `serial_test` for live-server serialization.

Risks: tests are ignored and depend on a manually running RustFS server. Several tests do not delete the bucket or ensure fixed keys are absent before setup, so stale state could affect the initial existence path. The code checks exact SDK service-error classification and will intentionally fail if transport/protocol errors leak out of RustFS.

Test signals: verifies deleted-object and never-existed-object reads return S3 service errors, not networking errors; verifies repeated reads remain stable after deletion; separately covers `GET` and `HEAD` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/get_deleted_object_test.rs -->
