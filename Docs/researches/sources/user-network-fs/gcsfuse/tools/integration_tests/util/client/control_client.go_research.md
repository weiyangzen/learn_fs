# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/control_client.go

## Purpose

Provides integration-test helpers around the GCS Storage Control API for managed folders and HNS folder creation. This client is used for test data setup, not application runtime behavior.

## Important APIs, control flow, and dependencies

`storageControlClientRetryOptions` configures gax timeout and retries for transient gRPC codes, including a temporary unauthenticated retry. `CreateControlClient` creates a `StorageControlClient` and sets create/delete managed folder call options. `CreateControlClientWithCancel` creates a cancelable context and close function. `DeleteManagedFoldersInBucket`, `CreateManagedFoldersInBucket`, and `CreateFolderInBucket` build Storage Control resource names and issue API requests.

## State, persistence, dependencies, and integration points

The helpers persist managed folder or HNS folder resources in the target bucket. They integrate with `setup.GetBucketAndObjectBasedOnTypeOfMount` and `internal/storage.FullBucketPathHNS` to respect only-dir mounts and HNS naming.

## Risks and test signals

Risks include fatal exits on setup failures, broad string matching for already-exists/not-found style errors, and a formatting bug in the `CreateControlClient` error string that uses `#{err}` instead of formatting `%v`. Signals are successful client creation, idempotent create/delete behavior for managed folders, and returned folder objects for HNS folder creation.
