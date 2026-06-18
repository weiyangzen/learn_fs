# sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs

Purpose: regression coverage for S3 conditional writes against a live RustFS server at `http://localhost:9000`. The tests validate `If-Match` and `If-None-Match` behavior for ordinary `PutObject` requests and `CompleteMultipartUpload`, including object-exists and object-missing cases.

Important APIs and functions: `create_aws_s3_client` builds an AWS SDK S3 client with static RustFS credentials, path-style addressing, and local endpoint override. `setup_test_bucket` creates `api-test` and tolerates `BucketAlreadyExists`. `generate_test_data` creates deterministic byte payloads; `upload_object_with_metadata` uploads and returns the response ETag; `cleanup_objects` best-effort deletes test keys; `generate_test_key` produces timestamped object keys.

Control flow: each ignored serial Tokio test creates the client and bucket, seeds object state, performs conditional write calls through AWS SDK builders, and checks either success or `SdkError::ServiceError` metadata. `test_conditional_put_okay` verifies matching `If-Match` and nonmatching `If-None-Match` succeed. `test_conditional_put_failed` verifies nonmatching `If-Match` and matching `If-None-Match` fail with `PreconditionFailed`. `test_conditional_put_when_object_does_not_exist` expects wildcard `If-Match` to fail with `NoSuchKey` but wildcard `If-None-Match` to create the object. `test_conditional_multi_part_upload` starts a multipart upload, sends three 5 MiB parts, and validates conditional completion failures before a matching `If-Match` success.

State and persistence: state is external S3 bucket/object data in a local RustFS instance. Most keys are unique except `some_key`, so `cleanup_objects` is used before and after. Multipart state persists through the upload ID until completion; the test does not abort after failed completion attempts, so server-side handling must keep the upload reusable.

Dependencies and integration points: AWS SDK S3, `bytes::Bytes`, `serial_test`, Tokio, RustFS S3 API, conditional request headers, ETag semantics, and multipart completion.

Risks: all tests are ignored and require a pre-running server, so CI will not catch regressions unless ignored tests are explicitly enabled. Bucket reuse can leak prior data if cleanup fails. The multipart test reuses the same `CompletedMultipartUpload` after failed completion calls, which depends on the server preserving upload state after precondition failure. `setup_test_bucket` does not accept `BucketAlreadyOwnedByYou`, unlike nearby tests.

Test signals: positive and negative assertion coverage for precondition matching, wildcard semantics for missing objects, `PreconditionFailed` error metadata, and multipart conditional completion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/conditional_writes.rs -->
