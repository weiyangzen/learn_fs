# sources/object-store/rustfs/crates/e2e_test/src/special_chars_test.rs

Purpose: end-to-end S3 compatibility coverage for object keys containing spaces, plus signs, percent signs, equals signs, Unicode, punctuation, and control characters. The file is entirely test code under `#[cfg(test)]`, using `RustFSTestEnvironment` to start a real RustFS server and `aws_sdk_s3::Client` for normal API calls.

Important APIs and flow: `create_s3_client`, `create_bucket`, and `signed_get` are local helpers. `signed_get` builds a raw `http::Request`, signs it with `rustfs_signer::sign_v4`, copies signed headers into `reqwest`, and validates canonical path/signature behavior for keys ending in `=`. Test cases then exercise `put_object`, `get_object`, `head_object`, `copy_object`, `delete_object`, and `list_objects_v2` with prefixes and delimiters.

State and persistence: each serial async test creates its own server process and bucket, writes objects into the test backend, verifies exact bytes/listing behavior, then calls `env.stop_server()`. No durable state should escape the test environment.

Dependencies and integration points: depends on the common e2e harness, AWS SDK S3 primitives, the local HTTP client, S3S `Body`, SigV4 signer, and `serial_test` to avoid cross-test server/bucket interference.

Risks: bucket names are mostly fixed, so failed cleanup or parallel external runs could collide despite `serial`. Some tests use `assert!(result.is_err())` rather than checking S3 error codes. Control-character coverage deliberately does not require tab rejection.

Test signals: strong regression signal for URL decoding/canonicalization, list-prefix delimiter behavior, raw signed requests, and common object operations over unusual key names.
