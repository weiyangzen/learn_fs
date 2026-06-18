# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_common_test.go

## Purpose

Defines the common stale-file-handle suite shared by local-file and empty-GCS-file scenarios. It verifies that gcsfuse reports ESTALE-like errors when an open file handle loses ownership because the backing object was clobbered or the path was renamed, while local unlink of an open file behaves like POSIX and does not upload stale content.

## Important APIs, control flow, and dependencies

`staleFileHandleCommon` embeds `suite.Suite` and carries flags, the active `*os.File`, generated file name, random 5 MiB payload, and booleans for streaming-writes and local-file modes. `SetupSuite` mounts gcsfuse with `setup.MountGCSFuseWithGivenMountWithConfigFunc`, sets the mounted directory, creates the GCS test directory with `client.SetupTestDirectory`, and generates test data. Tests use `operations.WriteWithoutClose`, `operations.SyncFile`, `operations.RenameFile`, `operations.ValidateESTALEError`, `operations.ValidateSyncGivenThatFileIsClobbered`, and GCS helpers from `util/client`.

## State, persistence, dependencies, and integration points

The suite explicitly maintains an open file handle while changing the namespace or backing object. `TestClobberedFileSyncAndCloseThrowsStaleFileHandleError` writes dirty local data, overwrites the GCS object generation, then expects sync/close to surface stale-handle behavior and preserve the clobbering GCS contents. `TestFileDeletedLocallySyncAndCloseDoNotThrowError` removes the path through the mount and verifies continued writes to the unlinked handle do not recreate the object. `TestRenamedFileSyncAndCloseThrowsStaleFileHandleError` renames the local path, expects further writes on the old handle to fail, and expects sync/close to be no-ops because no further data was accepted.

## Risks and test signals

The tests encode subtle differences between remote clobber, local unlink, and local rename. Zonal streaming-write takeover is skipped because unfinalized zonal object overwrite support is not ready. Strong signals are exact ESTALE validation, no-error validation for unlink, and final GCS content or not-found checks after each handle is closed.
