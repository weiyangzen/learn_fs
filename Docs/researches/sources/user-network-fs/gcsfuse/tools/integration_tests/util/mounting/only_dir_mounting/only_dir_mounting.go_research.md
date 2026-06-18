# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/only_dir_mounting/only_dir_mounting.go

Purpose: orchestrates integration tests for `--only-dir` mounts, including cases where the mounted prefix exists and does not exist in the bucket.

Important APIs/types/functions: `MountGcsfuseWithOnlyDirWithConfigFile`, deprecated `MountGcsfuseWithOnlyDir`, `executeTestsForOnlyDirMounting`, `mountGcsFuseForFlagsAndExecuteTests`, and `RunTestsWithConfigFile`.

Control flow: sets `setup.OnlyDirMounted`, deletes objects under the target prefix, runs each flag set, creates the prefix using storage-client helpers, runs the flag sets again, deletes the prefix, and resets only-dir state.

State/persistence behavior: mutates global only-dir state in `setup`, creates/deletes GCS objects under the test directory, mounts/unmounts gcsfuse, and writes trace logs.

Dependencies/integration: depends on `client.CreateStorageClient`, `client.DeleteAllObjectsWithPrefix`, `client.SetupTestDirectory`, and `mounting.MountGcsfuse`.

Risks/test signals: cleanup errors are logged with `%w` but through `log.Println`, so wrapping is ineffective. Because each flag set mounts and runs tests twice, failures can be sensitive to leftover bucket state or unmount failures.
