# sources/object-store/garage/src/garage/tests/admin.rs

Purpose: This integration test verifies that admin CLI bucket permission changes affect S3 authorization as expected for a live Garage instance.

Important APIs and types: `test_admin_bucket_perms` uses `common::context`, `aws_sdk_s3::Client::head_bucket`, and `CommandExt` on the Garage CLI. It exercises `bucket create`, `bucket allow --read`, `bucket deny --read`, and `bucket delete --yes`.

Control flow: The test starts with `head_bucket` failing for a missing bucket, creates the bucket, verifies it still fails before permission is granted, grants read permission to the test key, verifies success, denies read, verifies failure, grants read again, verifies success, deletes the bucket, and verifies failure again.

State and persistence behavior: The test mutates bucket metadata, bucket-key permission state, and bucket deletion state through CLI commands. S3 `head_bucket` observes those persisted table changes through the running daemon.

Dependencies and integration points: It bridges CLI admin operations, model permission tables, and S3 API authorization. It depends on the shared real-process integration harness and a single default test key.

Risks: The assertions are coarse because they only check success versus error, not exact S3 error codes. The bucket name is constant, so test isolation relies on the harness using a fresh test instance directory.

Test signals: Strong signals are the alternating `head_bucket` success/failure results after each permission or deletion operation, proving that admin metadata changes propagate to S3 authorization.
