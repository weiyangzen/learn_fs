<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs

Purpose: this E2E regression test verifies that `HeadObject` is consistent after both simple `PutObject` and completed multipart uploads, and that presigned HEAD URLs succeed against the local RustFS server.

Important APIs, types, and functions: `list_contains_key()` scans `ListObjectsV2Output.contents()` for a key. The test uses `RustFSTestEnvironment`, AWS SDK S3 `put_object`, `get_object`, `list_objects_v2`, `head_object`, multipart builders `CompletedMultipartUpload` and `CompletedPart`, `PresigningConfig`, and `local_http_client()` for a raw HEAD request to the presigned URI.

Control flow: the test starts a server, creates a fixed bucket, writes a normal object, confirms `GetObject` and `ListObjectsV2` can see it, then calls `HeadObject`. It creates a multipart upload for another key, uploads one part, completes it using the returned ETag, confirms `GetObject` and `ListObjectsV2` see the completed key, then calls `HeadObject` for that key. Finally it presigns a HEAD request for the first key and verifies the raw HTTP status is success before deleting objects and bucket.

State and persistence: persistent state is limited to two objects and multipart upload metadata in the test bucket. The test intentionally checks data-plane/listing visibility before HEAD, so a HEAD failure after those checks indicates a metadata lookup path inconsistency rather than write failure.

Dependencies and integration points: depends on AWS SDK presigning, local reqwest client support, RustFS S3 object, multipart, list, head, and SigV4 presigned request handling. `serial_test` avoids shared fixed bucket conflicts.

Risks: fixed bucket/key names require serial isolation. Multipart uses a single small part, which may not cover all multi-part layout behavior even though it covers completed MPU metadata. The presigned check only validates success status, not headers.

Test signals: success demonstrates HEAD visibility after simple writes and completed MPU, list/head consistency for both key types, and working presigned HEAD authentication over the raw HTTP path.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_consistency_test.rs -->
