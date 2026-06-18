# sources/object-store/garage/src/garage/tests/s3/mod.rs

Purpose: This module declares the S3 integration test suite.

Important APIs and types: It includes submodules `cors`, `list`, `multipart`, `objects`, `presigned`, `signature_encoding`, `simple`, `ssec`, `streaming_signature`, and `website`.

Control flow: Normal Rust module inclusion makes the child tests visible to the integration test crate.

State and persistence behavior: This file has no state. Child modules create buckets, objects, multipart uploads, CORS/website configs, and encrypted objects.

Dependencies and integration points: It is included from `tests/lib.rs` and is the aggregator for S3 API coverage against the live Garage daemon.

Risks: New S3 test files must be declared here. Because all children share the singleton integration instance, child tests should use unique bucket names to avoid cross-test contamination.

Test signals: Successful compilation ensures all listed S3 test modules participate in the integration suite.
