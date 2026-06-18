<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs -->
## sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs

Purpose: this compact E2E regression test ensures `HeadObject` advertises byte-range support through the `Accept-Ranges: bytes` response metadata.

Important APIs, types, and functions: the test uses `RustFSTestEnvironment`, AWS SDK S3 `put_object`, `head_object`, `delete_object`, and the constants `RANGE_HEAD_BUCKET`, `RANGE_HEAD_KEY`, and `ACCEPT_RANGES_BYTES`.

Control flow: the test starts a RustFS server, creates a bucket, uploads a small binary object, issues `HeadObject`, asserts `head.accept_ranges() == Some("bytes")`, deletes the object, deletes the bucket, and stops the server.

State and persistence: state is one bucket and one object. No long-lived state should remain after cleanup. The tested behavior is response-header metadata derived from object capability rather than object content.

Dependencies and integration points: depends on AWS SDK S3 head response mapping, RustFS HEAD object implementation, and the common environment helpers. `serial_test` protects the fixed bucket name.

Risks: the test checks only positive behavior for an existing object and does not inspect raw HTTP casing or other HEAD headers. Fixed names require isolation. A missing cleanup on assertion failure can leave the temporary bucket until environment teardown.

Test signals: a passing run confirms AWS SDK observes `AcceptRanges` as `bytes`, which means RustFS emits the expected range-advertisement header for normal objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/head_object_range_test.rs -->
