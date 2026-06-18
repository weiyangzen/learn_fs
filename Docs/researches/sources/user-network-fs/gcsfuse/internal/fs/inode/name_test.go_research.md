# sources/user-network-fs/gcsfuse/internal/fs/inode/name_test.go

Purpose: verifies the `inode.Name` contract for root, directory, file, descendant, map-key, and parent-name behavior. It is an external package test (`inode_test`) and therefore exercises the exported API surface rather than private fields.

Important tests: `TestName` runs the same scenarios for single-bucket mounts (`bucketName == ""`) and multi-bucket local names (`bucketx/`). It constructs root, nested directories, root files, nested files, and a descendant name, then checks `IsBucketRoot`, `IsDir`, `IsFile`, `GcsObjectName`, `LocalName`, and `IsDirectChildOf`. `TestNameAsMapKey` confirms that `Name` is comparable and can safely be used as a Go map key. `TestParentName` covers parent resolution for directory and file names at several depths. `TestParentNameReturnsErrorOnBucketRoot` asserts the explicit root error.

Control flow and state: the tests are table-like but written inline, with assertions repeated for both bucket modes. No filesystem or GCS state is created; all behavior is deterministic value semantics. The parent-name checks compare both GCS object names and local names, which catches bucket-prefix mistakes as well as object-name mistakes.

Dependencies and integration: uses `github.com/googlecloudplatform/gcsfuse/v3/internal/fs/inode` plus ogletest/oglematchers assertions. These tests protect callers in directory lookup, rename, symlink, and listing code from path-shape regressions.

Risks and coverage gaps: the tests do not assert the panic paths in `NewDirName` or `NewFileName`, nor the weak validation behavior of `NewDescendantName`. They also do not exercise child names that already contain slashes except by passing `"child/"` in a separate recursive-cancellation test through `NewDirName`, which the constructor normalizes only by ensuring a final slash.

Test signals: the strongest signal is dual-mode coverage of local path prefixing. Any change that alters trailing-slash directory representation, direct-child detection, or parent trimming will fail here.
