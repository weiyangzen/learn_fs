# sources/object-store/rustfs/crates/e2e_test/src/data_usage_test.rs

## Purpose
This ignored e2e regression test checks data-usage accuracy for issue #1012 by uploading 1000 objects and verifying the admin data-usage API reports at least that many objects globally and per bucket.

## Important APIs, Types, and Functions
The test imports `rustfs_data_usage::DataUsageInfo` to deserialize the admin response, uses AWS SDK `ByteStream` for uploads, and uses `awscurl_get` to call `/rustfs/admin/v3/datausageinfo`.

## Control Flow
When explicitly enabled, the test starts RustFS, creates `TEST_BUCKET`, uploads keys `obj-0000` through `obj-0999`, fetches admin data usage JSON, deserializes it, obtains the bucket usage entry, and asserts both total and bucket object counts are at least 1000.

## State and Persistence
State includes a test bucket with 1000 small objects and whatever data-usage snapshot/cache the server maintains. The test reads admin usage state rather than directly scanning storage.

## Dependencies and Integration Points
The file connects S3 object writes, admin API signing through awscurl, and the shared `rustfs-data-usage` response model. It is registered in `src/lib.rs` but marked `#[ignore]`.

## Risks and Edge Cases
Because it is ignored by default and requires awscurl, it is not part of normal test runs. The assertions allow counts greater than 1000, which tolerates extra accounting but would not detect overcounting. It does not wait or force a scanner cycle, so runtime behavior may depend on when data usage is updated.

## Test Signals
The key signal is absence of truncation: `objects_total_count >= 1000` and `bucket_usage.objects_count >= 1000` after uploading 1000 objects.
