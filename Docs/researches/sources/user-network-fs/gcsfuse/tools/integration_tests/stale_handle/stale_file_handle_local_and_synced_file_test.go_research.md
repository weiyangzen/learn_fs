# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_local_and_synced_file_test.go

## Purpose

Adds concrete stale-handle suites for two starting states: a purely local file created through the mount and an empty object that already exists in GCS. It also provides the package entry points that run those suites under streaming-writes enabled and disabled flag configurations.

## Important APIs, control flow, and dependencies

`staleFileHandleLocalFile.SetupTest` creates a unique local file with `operations.OpenFileWithODirect`. `staleFileHandleEmptyGcsFile.SetupTest` creates an empty GCS object with `client.CreateObjectOnGCS`, validates it, and opens it through the mount. Additional empty-GCS tests cover read after remote clobber, first write after remote clobber, and remote delete while the file handle is dirty. `TestStaleHandleStreamingWritesEnabled` and `TestStaleHandleStreamingWritesDisabled` either run directly for mounted-directory mode or iterate over `setup.BuildFlagSets` for the configured bucket type.

## State, persistence, dependencies, and integration points

The tests coordinate three state sources: the open local file descriptor, the mounted namespace, and the underlying object generation in GCS. Remote clobber uses `WriteToObject` without matching the handle generation; remote delete uses `DeleteObjectOnGCS`. Each suite saves gcsfuse logs on failure and relies on the common suite for mount lifecycle.

## Risks and test signals

The riskiest paths are generation takeover and flushing dirty data after the remote object disappears. Zonal streaming-write cases are skipped for known takeover and client bugs. Signals include ESTALE on reads or close after clobber, successful writes before stale detection where the implementation accepts buffering, unchanged clobbering contents in GCS, and object-not-found validation after remote delete.
