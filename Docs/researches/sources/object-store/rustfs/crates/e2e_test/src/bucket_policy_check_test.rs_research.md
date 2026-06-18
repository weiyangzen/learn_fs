# sources/object-store/rustfs/crates/e2e_test/src/bucket_policy_check_test.rs

## Purpose
This regression test verifies that bucket policies granting an authenticated user access are honored for list, put, get, and delete operations. It targets issue #1423 around authenticated-user policy evaluation.

## Important APIs, Types, and Functions
`create_user` calls the admin add-user endpoint using `awscurl_put` with JSON containing `secretKey` and enabled status. `create_user_client` builds an AWS S3 client with the new user's credentials. The test applies a bucket policy with `Principal: {"AWS": [user_access]}` and actions `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject`.

## Control Flow
The test skips if awscurl is unavailable, starts RustFS, creates a bucket as admin, creates a user through the admin API, verifies the user cannot list before policy installation, installs the policy as admin, then verifies the user can put, list, get, and delete the target object.

## State and Persistence
State includes the temporary server data, an IAM-style user credential, a bucket, a bucket policy, and one object. User and policy metadata are persisted inside the test server's data directory.

## Dependencies and Integration Points
The test integrates admin user-management APIs, awscurl SigV4 requests, AWS SDK S3 clients with non-admin credentials, bucket policy authorization, and S3 object operations.

## Risks and Edge Cases
The test checks a single allow policy and does not cover deny precedence, wildcard principals, ARNs with account ids, policy variables, or conditions. It only asserts the initial no-policy call fails, not a specific error code.

## Test Signals
The strongest signal is the transition from denied list access before policy to successful put/list/get/delete after policy. Skipping when awscurl is unavailable is an explicit test-environment signal.
