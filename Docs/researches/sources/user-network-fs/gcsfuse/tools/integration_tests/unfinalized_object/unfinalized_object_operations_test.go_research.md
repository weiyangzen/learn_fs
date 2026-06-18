# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_object_operations_test.go

## Purpose

Covers non-read operations and metadata behavior for unfinalized zonal objects: visible nonzero sizes, same-mount creation and finalization, rename semantics, inode preservation on remote append, and inode change on remote overwrite.

## Important APIs, control flow, and dependencies

`unfinalizedObjectOperations` manages suite mount lifecycle and per-test setup. Helper `setupUnfinalizedObjectAndGetInitialInode` creates an unfinalized object and stats it with `operations.StatFileOrFatal`. Tests use `client.CreateUnfinalizedObject`, `operations.CreateFile`, `WriteWithoutClose`, `SyncFile`, `StatFile`, `RenameFile`, `AppendableWriter`, object attrs, and GCS validation helpers.

## State, persistence, dependencies, and integration points

Tests distinguish same-generation append from generation-changing overwrite. A remote append should update size while preserving inode ID; a remote overwrite should change the inode. Same-mount unfinalized creation writes and syncs without final close, then additional writes and close finalize the object. Rename tests verify object movement and stale-handle behavior for old file descriptors.

## Risks and test signals

Risks include known skipped overwrite behavior (`b/411333280`), incorrect inode identity when generation does not change, and rename of unfinalized objects from different mounts. Signals are nonzero stat sizes, final size doubling after close, object-not-found for renamed source, exact content at destination, ESTALE after writing through a stale handle, preserved generation on append, and changed inode on overwrite.
