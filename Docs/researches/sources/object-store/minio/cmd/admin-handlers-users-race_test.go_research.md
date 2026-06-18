# sources/object-store/minio/cmd/admin-handlers-users-race_test.go

## Purpose
`admin-handlers-users-race_test.go` contains the slow IAM concurrency test suite for deleting users while their credentials are still attempting S3 access. Despite the filename, it is explicitly excluded under Go's `-race` build tag because the suite is too slow and can hit context deadlines when the race detector is enabled.

## Important APIs, Types, And Functions
The file defines `runAllIAMConcurrencyTests`, `TestIAMInternalIDPConcurrencyServerSuite`, and the method `TestSuiteIAM.TestDeleteUserRace`. It reuses `TestSuiteIAM` and helper assertions from `admin-handlers-users_test.go`.

The test matrix covers ErasureSD, ErasureSD with TLS, Erasure, and ErasureSet backends, each with and without etcd IAM backend. It skips Windows via `globalWindowsOSName`.

`TestDeleteUserRace` uses `madmin.AdminClient` methods `AddCannedPolicy`, `SetUser`, `AttachPolicy`, and `RemoveUser`, a MinIO S3 client for bucket access, and `github.com/minio/pkg/v3/sync/errgroup` to run many deletion/access checks concurrently.

## Control Flow
The suite setup mirrors the main IAM test suite: initialize a MinIO test server, optionally configure etcd-backed IAM, run the concurrency test, then tear down. `TestDeleteUserRace` creates a bucket, adds a policy permitting list/get/put on that bucket, creates 50 users, attaches the policy to every user, then starts 50 goroutines.

Each goroutine builds a user S3 client from that user's credentials, removes the user through the admin client, and then asserts that the deleted user's client can no longer list objects in the bucket. The errgroup aggregates remove/list failures and fails the test on any non-empty error set.

## State And Persistence Behavior
The test exercises concurrent IAM mutation and credential invalidation. It creates persistent users, policy mappings, and a canned policy, then concurrently deletes users while immediately attempting S3 authorization with credentials that were valid moments earlier. With etcd enabled, the same behavior is exercised through the etcd-backed IAM store; otherwise it uses the local IAM backend configured by the test server.

The key persistence signal is that `RemoveUser` must fully remove or invalidate the user's IAM identity and policy mapping quickly enough that subsequent authorization fails. The test does not explicitly clean up the policy or bucket because the test server teardown owns fixture cleanup.

## Dependencies And Integration Points
The file depends on the IAM admin APIs implemented in `admin-handlers-users.go`, the shared `TestSuiteIAM` setup in `admin-handlers-users_test.go`, MinIO S3 client behavior, madmin client behavior, and the optional `_MINIO_ETCD_TEST_SERVER` setup path. It integrates with backend variants to catch differences between local and etcd IAM persistence.

## Risks And Test Signals
The test is expensive and time-sensitive: it uses a 90-second context and 50 concurrent user removals, and it is disabled under race-detector builds. A failure can indicate IAM cache invalidation races, stale policy mappings, etcd propagation delays, or incorrect `RemoveUser` cleanup. The strongest signal is that a deleted credential must receive an error when listing the bucket immediately after deletion, even under concurrent admin operations.
