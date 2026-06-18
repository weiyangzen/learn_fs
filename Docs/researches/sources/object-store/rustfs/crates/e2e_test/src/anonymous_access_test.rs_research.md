# sources/object-store/rustfs/crates/e2e_test/src/anonymous_access_test.rs

## Purpose
This regression suite verifies anonymous `GetObject` access behavior when a bucket policy allows public reads and PublicAccessBlock configuration is missing, enabled, or explicitly disabled. It covers issue #2036 around missing PublicAccessBlock config incorrectly blocking anonymous policy access.

## Important APIs, Types, and Functions
`setup_public_bucket` creates a bucket, installs an allow-anonymous `s3:GetObject` policy for `bucket/*`, uploads `test.txt`, and returns the admin S3 client. `anonymous_get_object` uses `reqwest` without credentials through `local_http_client`. Tests use AWS SDK `PublicAccessBlockConfiguration`.

## Control Flow
Each test starts a single RustFS server, prepares a public bucket, sets or deletes PublicAccessBlock state, performs an unsigned HTTP GET, and asserts the status code. Missing config and `restrict_public_buckets(false)` expect 200; `restrict_public_buckets(true)` expects 403.

## State and Persistence
The tests create temporary RustFS storage, buckets, one object, bucket policies, and optional PublicAccessBlock configuration. State is cleaned when `RustFSTestEnvironment` drops or `stop_server` runs.

## Dependencies and Integration Points
The file integrates bucket policy authorization, PublicAccessBlock evaluation, AWS SDK S3 control APIs, and raw anonymous HTTP reads. It depends on `common.rs` for server lifecycle and proxy-free HTTP.

## Risks and Edge Cases
Bucket names are fixed per test, so `serial` is required to avoid conflicts. The tests validate only `RestrictPublicBuckets`, not all PublicAccessBlock flags. They assert status codes but do not inspect error XML codes.

## Test Signals
The status-code matrix is the main signal: 200 when configuration is absent, 403 when public buckets are restricted, and 200 when restriction is explicitly disabled.
