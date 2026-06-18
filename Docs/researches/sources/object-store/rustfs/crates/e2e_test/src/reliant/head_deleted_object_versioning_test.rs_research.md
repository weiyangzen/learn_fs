# sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs

Purpose: live-server regression coverage for `HeadObject` when bucket versioning is enabled and the latest version is a delete marker. It addresses a prior behavior where RustFS returned `200 OK` instead of a missing-object response.

Important APIs and functions: `create_aws_s3_client` builds the localhost AWS SDK client. `setup_test_bucket` creates `test-head-deleted-versioning-bucket`, accepts existing-bucket errors, then enables versioning with `put_bucket_versioning` and `VersioningConfiguration { status: Enabled }`. The single test uses `put_object`, `delete_object`, and `head_object`.

Control flow: the test initializes tracing, creates/enables the bucket, uploads `test-head-deleted-versioning.txt`, deletes it to create a delete marker, then performs `HeadObject` without an explicit version ID. It asserts a service error and accepts `NoSuchKey`, `NotFound`, or raw `404` error codes.

State and persistence: the important persisted state is bucket versioning plus the delete marker produced by the delete operation. Because the bucket and key are fixed and versioning is never suspended or cleaned up, previous runs can leave historical versions behind. The test relies on latest-version semantics, so historical versions should not make the unversioned `HEAD` succeed if delete-marker handling is correct.

Dependencies and integration points: AWS SDK S3 versioning types, RustFS versioned object metadata/delete-marker logic, error metadata mapping for `HEAD`, `serial_test`, and live localhost server setup.

Risks: ignored by default and dependent on external RustFS. The broad accepted error-code set improves compatibility but reduces precision. The fixed bucket can accumulate versions across runs.

Test signals: validates unversioned `HEAD` observes the current delete marker and reports missing-object semantics instead of exposing an older live version.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_deleted_object_versioning_test.rs -->
