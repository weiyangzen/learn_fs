# sources/object-store/garage/src/garage/tests/bucket.rs

Purpose: This integration test exercises basic bucket lifecycle and create-bucket permission behavior through the AWS S3 SDK against a live Garage instance.

Important APIs and types: `test_bucket_all` uses AWS SDK operations `create_bucket`, `list_buckets`, `get_bucket_location`, `get_bucket_versioning`, and `delete_bucket`, plus CLI `key deny/allow --create-bucket`. It asserts `DeleteBucketOutput` equality for the delete result.

Control flow: The test first denies the key create-bucket capability and expects S3 bucket creation to fail. It then grants create-bucket, creates `hello`, checks the returned location, lists buckets to find it, reads bucket location, checks the versioning stub returns no status, deletes the bucket, and confirms it disappears from listing.

State and persistence behavior: The test mutates key-level create-bucket permissions and bucket alias/object-store metadata. No objects are written, so deletion is expected to succeed without non-empty-bucket handling.

Dependencies and integration points: It ties key permission state from the admin CLI to S3 CreateBucket authorization and validates the bucket listing/location/versioning API surface provided by Garage.

Risks: The test does not assert exact error codes for unauthorized creation and leaves TODOs for invalid names, duplicate bucket creation, and non-empty bucket deletion. Constant bucket names require a clean integration instance.

Test signals: CreateBucket failure before permission, success after permission, `/hello` location, region `garage-integ-test`, empty versioning status, and absence from `ListBuckets` after deletion.
