# sources/object-store/rustfs/crates/e2e_test/src/multipart_auth_test.rs

## Purpose

This Rust end-to-end test module is a broad S3 compatibility regression suite for RustFS request handling around anonymous multipart-related APIs, browser-style POST object uploads, unsupported write-offset PUTs, and signed PUT archive auto-extraction. The opening module comment names anonymous multipart control API coverage, but the file has grown into a larger object-ingest conformance suite. It verifies that RustFS:

- Rejects anonymous multipart control operations such as AbortMultipartUpload, ListParts, CompleteMultipartUpload, and UploadPartCopy with HTTP 403.
- Rejects unauthenticated POST object uploads unless bucket policy explicitly grants anonymous `s3:PutObject`.
- Enforces POST policy coverage and exact/starts-with/content-length conditions for form fields that map to S3 object metadata, response behavior, storage class, encryption, checksum, object lock, tagging, bucket, and SigV4-like form fields.
- Persists accepted POST object fields into object state observable through `head_object`, `get_object`, `get_object_tagging`, `get_object_retention`, and `get_object_legal_hold`.
- Rejects unsupported headers such as `x-amz-write-offset-bytes` with MinIO-compatible `NotImplemented` XML without creating objects.
- Expands uploaded tar-family archives when snowball auto-extract headers are present, preserving or rejecting object attributes according to RustFS support.

The tests are integration tests rather than library code: they start a RustFS server, create buckets, mutate bucket policy/configuration, make SDK and raw HTTP requests, and assert on wire-level status codes, XML error codes, response headers, persisted object bytes, metadata, tags, encryption state, object lock state, version IDs, and archive-extracted keys.

## Important APIs, Helpers, and Types

- `RustFSTestEnvironment`, `init_logging`, and `local_http_client` come from `crate::common`. Each test starts an isolated RustFS server with `env.start_rustfs_server(vec![]).await?`, creates an AWS SDK S3 client with `env.create_s3_client()`, and uses the local reqwest client for raw unauthenticated or form requests.
- `encode_post_policy(conditions)` creates a base64 JSON POST policy with an expiration one hour in the future and the provided policy condition list. It is the shared setup for tests that need form-level policy validation.
- `sse_customer_key_md5_base64(key)` computes the base64 MD5 for SSE-C customer keys, used by POST and archive-extraction tests that need SSE-C headers.
- `make_tar(files, dirs)` builds in-memory tar archives using `tokio_tar`, supporting both file entries and directory entries.
- `build_pax_record` and `make_tar_with_pax_entry` construct PAX extended headers, including `minio.metadata.*`, `minio.versionId`, and file modification timestamps, for archive extraction tests.
- `gzip_bytes`, `zstd_bytes`, `bzip2_bytes`, and `xz_bytes` generate compressed tar payloads for `.tar.gz`, `.tgz`, `.tzst`, `.tbz2`, and `.txz` extraction coverage.
- `assert_s3_error_code(result, code)` normalizes AWS SDK `SdkError` assertions to service error metadata codes.
- `signed_raw_request` manually builds an HTTP request, sets `Host` and `x-amz-content-sha256: UNSIGNED-PAYLOAD`, signs it with `rustfs_signer::sign_v4`, then sends it through reqwest. It is used where the test must inspect the raw HTTP body instead of relying on AWS SDK error mapping.
- `allow_anonymous_put_object(client, bucket)` installs a bucket policy that grants public `s3:PutObject` on `arn:aws:s3:::bucket/*`, enabling anonymous POST/PUT tests to isolate form policy behavior from authorization denial.

Major imported dependencies include `aws_sdk_s3` request builders and S3 types, `reqwest::multipart` for browser POST forms, `rustfs_signer` for raw SigV4 signing, `tokio_tar` for archive creation, compression crates for archive formats, `chrono` for policy expiration, `base64` and `md5` for policy/SSE values, `uuid` for version ID checks, and `serial_test::serial` to keep tests from racing over local server resources.

## Control Flow

All tests follow a consistent integration-test flow:

1. Initialize logging.
2. Create and start a fresh `RustFSTestEnvironment`.
3. Create an S3 bucket through the admin SDK client.
4. Optionally configure bucket policy, bucket default encryption, bucket versioning, or object lock.
5. Build either an SDK request, a reqwest multipart form, or a raw signed HTTP request.
6. Send the request to RustFS.
7. Assert the immediate response status/error code.
8. When the request is expected to succeed, verify persisted object state through read-side S3 APIs.
9. When the request is expected to fail, often verify that no object was created.

The first test, `test_anonymous_multipart_control_apis_require_auth`, seeds a source object for copy, then sends raw anonymous DELETE, GET, POST XML, and PUT-with-copy-source requests with a dummy upload ID. Its control flow deliberately avoids creating a real multipart session, because the regression under test is auth gating before multipart state handling.

The POST object tests form the largest control-flow matrix. Basic cases verify required authorization, `success_action_status` 201 XML responses, `success_action_redirect` 303 responses with location query parameters, and the default 204 empty-body response. The policy tests then vary one form field at a time:

- A matching exact condition generally succeeds and is verified through persisted object state.
- A submitted `x-amz-*` or response-control field missing from policy conditions generally returns 403 `AccessDenied`.
- A submitted field covered by an exact policy condition but with a conflicting value generally returns 400 `InvalidPolicyDocument` and a diagnostic mentioning the field.
- `starts-with` and `content-length-range` conditions test prefix acceptance/rejection and object size limits.
- Invalid storage class values return `InvalidStorageClass`, not merely a policy mismatch.
- Certain fields are intentionally exempt or special-cased, such as ignored `x-ignore-*` fields and SSE-C fields accepted outside policy coverage.

The signed PUT/write-offset tests split into SDK and raw HTTP paths. SDK calls assert service metadata code `NotImplemented`; raw signed and anonymous HTTP calls assert the wire status and XML body, then verify rejected writes do not create objects. A follow-up anonymous plain PUT validates that the bucket policy remains capable of allowing normal unauthenticated writes when the unsupported header is absent.

The archive-extraction tests upload tar or compressed-tar payloads with snowball auto-extract headers. Their control flow is: synthesize an archive, put the archive object with metadata headers that request extraction, then fetch or head extracted objects under the requested or default key prefix. Negative cases assert `InvalidStorageClass`, `NotImplemented`, or `InvalidArgument` from the PUT itself.

## State and Persistence Behavior

This file heavily verifies persisted object metadata and bucket state:

- Anonymous POST success writes object bytes exactly as supplied in the `file` multipart part.
- POST response behavior does not replace object persistence: tests fetch the object after 201, 204, and redirect responses.
- SSE-S3 POST uploads persist `server_side_encryption = AES256`; bucket default SSE-S3 and default SSE-KMS are also observed on uploaded objects.
- SSE-KMS form fields are accepted through policy validation in some cases but ultimately rejected with `NotImplemented`, while default SSE-KMS for normal POST succeeds in the tested environment and archive extraction with bucket-default KMS is rejected.
- SSE-C POST and extraction paths require customer algorithm, key, and MD5 on subsequent `head_object`/`get_object` calls, proving encrypted object state is created.
- Storage class, cache control, content type, content disposition, content language, content encoding, website redirect location, `Expires`, user metadata, object tags, legal hold, retention mode/date, and version ID are read back from S3 APIs.
- Object lock tests create buckets with `object_lock_enabled_for_bucket(true)` before verifying retention and legal hold state.
- Archive extraction creates separate objects for tar entries and, by default, directory marker objects. The ignore-dirs option skips directory markers; ignore-errors skips invalid entries while retaining valid extracted keys.
- PAX metadata extraction maps `minio.metadata.project` and `minio.metadata.x-amz-meta-owner` onto S3 user metadata and preserves `minio.versionId` when bucket versioning is enabled.
- Rejected write-offset PUTs explicitly leave no object at the target key, while later normal PUTs can create the object.

The tests do not inspect RustFS internals or disk layout. Persistence is observed entirely through S3 API behavior against the local test server.

## Dependencies and Integration Points

The module integrates with:

- The e2e test harness in `crate::common` for server lifecycle, credentials, endpoint URL, and HTTP client construction.
- AWS SDK S3 operation builders for bucket creation, policy, encryption, versioning, PUT/GET/HEAD, tagging, object lock, and customized request mutation.
- Raw HTTP endpoints for anonymous multipart control API calls and browser-compatible POST forms.
- RustFS authorization and bucket policy evaluation through anonymous `s3:PutObject` policies.
- RustFS POST object policy parsing and validation, including exact-match JSON object conditions, array conditions like `starts-with` and `content-length-range`, field coverage requirements, duplicate field detection, and error mapping.
- RustFS object write pipeline for encryption, object lock, metadata, tags, storage class, redirect metadata, and checksum-related form fields.
- RustFS unsupported-feature mapping for SSE-KMS archive extraction and write-offset PUT headers.
- RustFS snowball/archive auto-extract support triggered by metadata headers including `x-amz-meta-snowball-auto-extract`, `x-amz-snowball-auto-extract`, `x-amz-meta-acme-snowball-prefix`, `x-amz-meta-rustfs-snowball-prefix`, `x-amz-meta-snowball-prefix`, `x-amz-meta-acme-snowball-ignore-dirs`, and `x-amz-meta-acme-snowball-ignore-errors`.

Because the tests use both SDK-level assertions and raw HTTP/body assertions, they exercise both high-level S3 compatibility and exact MinIO-compatible XML response shapes.

## Risks and Edge Cases

- The file is very large and has repeated setup logic. Adding new POST policy fields can easily miss one of the expected categories: allowed exact match, missing condition denial, mismatch invalid-policy error, and persisted readback.
- Tests are all marked `#[serial]`, which avoids shared local server contention but makes the suite expensive; failures may be time-consuming to reproduce.
- Some behavior is intentionally nuanced: SSE-C fields are allowed outside policy coverage, `x-ignore-*` fields are ignored, SSE-KMS may pass policy validation before runtime `NotImplemented`, and missing-vs-mismatched fields map to different error classes. These are compatibility traps for refactors.
- Raw signed requests depend on correct `Host`, unsigned payload handling, region string, and local credentials. Changes to signer behavior or endpoint URI formatting could break tests without any server behavior regression.
- Archive extraction relies on extension-based format detection; missing extensions and invalid compressed payloads are expected `InvalidArgument` cases.
- PAX metadata ordering comes from a `HashMap`, but the generated PAX records are independent key/value records, so the tests do not assert on archive byte determinism except in the archive ETag test, which uses a simple tar from `make_tar`.
- The archive ETag test expects the PUT response ETag to be the MD5 of the original archive upload, not a derived ETag for extracted objects.
- Bucket names are hard-coded and numerous. The fresh environment and serial execution are important to avoid bucket-name collisions.
- Several assertions accept multiple missing-object codes (`NoSuchKey`, `NoSuchVersion`, or `NotFound`) where the server may differ from AWS SDK normalization.

## Test Signals

Strong positive test signals include:

- HTTP status assertions for forbidden anonymous multipart controls, POST auth failures, POST policy failures, unsupported features, redirects, and successful 204/201 responses.
- XML body checks for `AccessDenied`, `InvalidPolicyDocument`, `InvalidStorageClass`, `NotImplemented`, `EntityTooLarge`, and `InvalidArgument`.
- Persisted object body equality after successful POST and extraction.
- `head_object` checks for encryption, storage class, content headers, website redirect, expiration, custom metadata, last-modified from tar mtime, and version ID from PAX.
- `get_object_tagging`, `get_object_retention`, and `get_object_legal_hold` checks for secondary object state.
- Negative persistence checks after rejected write-offset requests.
- ListObjects verification that ignore-errors extraction only stores the valid entry.

Notable coverage gaps visible from the file:

- Multipart initiation and authenticated multipart upload success paths are not covered here, only anonymous control API rejection with a dummy upload ID.
- POST policy expiration, malformed base64/JSON policy, and signed POST credential validation are not comprehensively covered beyond form-field mismatch conditions.
- Archive extraction is covered for several formats and attributes, but not for path traversal, symlink/hardlink handling, extremely large archives, or concurrent extraction.
- The tests verify local single-server behavior except where the shared harness itself may simulate more; cluster namespace lock behavior is covered separately in `namespace_lock_quorum_test.rs`.
