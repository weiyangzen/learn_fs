# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/dir_operations.go

Purpose: directory and bucket-management helpers for integration tests.

Important APIs/types/functions: permission constants, `CopyDir`, `CopyObject`, `Move`, `RenameDir`, `CreateDirectoryWithNFiles`, `RemoveDir`, `ReadDirectory`, verification helpers, `CreateDirectory`, `DirSizeMiB`, managed-folder helpers, and `CopyFileInBucket`.

Control flow: simple operations use OS commands or filesystem calls; `CreateDirectoryWithNFiles` creates many files concurrently with a bounded 1024-goroutine semaphore and reports the first create error through a buffered channel.

State/persistence behavior: creates, renames, removes, and lists local or mounted directories, and invokes `gcloud alpha storage` commands for managed folders and bucket file copy. These calls modify local filesystem, mounted gcsfuse view, and remote GCS bucket state.

Dependencies/integration: used by integration test packages that need large directory structures or managed folders. Uses `ExecuteGcloudCommand` from the same package.

Risks/test signals: shelling out to `cp`, `mv`, and `gcloud` makes behavior platform/tool dependent. `DirSizeMiB` assumes non-nil `info` in `filepath.Walk` even when an error is passed to the callback.
