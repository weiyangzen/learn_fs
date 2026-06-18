# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/rename_file_test.go

## Purpose

Validates rename interactions with streaming writes, including renaming after data has been synced but before close and syncing an already-open handle after its path has moved.

## Important APIs, control flow, and dependencies

`TestRenameBeforeFileIsFlushed` writes twice, verifies stat size, calls `Sync`, renames the path, validates new GCS object contents, closes the original handle, and verifies the old object is gone. `TestSyncAfterRenameSucceeds` writes once, syncs, renames, calls `Sync` again on the old handle, validates the renamed object, and closes. Dependencies are `operations.WriteWithoutClose`, `operations.VerifyStatFile`, `operations.RenameFile`, GCS validation helpers, and testify `require`.

## State, persistence, dependencies, and integration points

The tests keep the file descriptor open across namespace moves. They require gcsfuse to bind the streaming upload state to the file content while updating object names and deleting old names in GCS.

## Risks and test signals

Risks include data being uploaded under the old object name, stale file handle errors on benign post-rename sync, and premature close failures. Signals are no rename/sync errors, exact content under the new name, successful close, and object-not-found for the original name.
