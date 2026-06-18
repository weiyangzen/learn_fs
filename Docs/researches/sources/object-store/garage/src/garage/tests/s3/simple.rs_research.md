# sources/object-store/garage/src/garage/tests/s3/simple.rs

Purpose: This is the basic S3 smoke test for object write/read.

Important APIs and types: `test_simple` uses `common::context`, AWS SDK `put_object`/`get_object`, `ByteStream`, and `assert_bytes_eq!`.

Control flow: The test creates a bucket, uploads `Hello world!` under key `test`, reads the object back, and compares the response body bytes.

State and persistence behavior: It persists one object in a new bucket and reads it back immediately.

Dependencies and integration points: It validates the minimal path through bucket creation/permission setup, AWS SDK signing, S3 PUT object storage, and S3 GET object retrieval.

Risks: It is intentionally narrow and does not inspect headers, ETags, metadata, ranges, or error behavior. It assumes immediate consistency in the single-node test setup.

Test signals: Successful PUT, successful GET, and exact body equality.
