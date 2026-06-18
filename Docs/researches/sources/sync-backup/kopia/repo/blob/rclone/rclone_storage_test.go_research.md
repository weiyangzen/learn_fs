# sources/sync-backup/kopia/repo/blob/rclone/rclone_storage_test.go

Purpose: integration tests for the rclone provider, including process startup/failure and provider-backed storage behavior.

Important APIs/types/functions: `mustGetRcloneExeOrSkip`, `TestRCloneStorageCancelContext`, `TestRCloneStorage`, `TestRCloneStorageDirectoryShards`, `Killable`, `TestRCloneStorageInvalidExe`, `TestRCloneStorageInvalidFlags`, `TestRCloneProviders`, and `cleanupOldData`.

Control flow: tests locate an rclone executable or skip, create temporary/local or external provider remotes, run shared blob storage tests through the rclone provider, test context cancellation during startup, verify invalid executable/flags fail, exercise directory sharding, and clean stale remote test data.

State and persistence behavior: tests launch real rclone processes, create temp dirs/configs, and mutate local or configured remote storage. Cleanup removes old blobs and provider temp state.

Dependencies/integration points: validates external process orchestration, WebDAV delegation, RC cache flushing, and generic blob behavior. Risks include environment-dependent skips, rclone version/output changes breaking regexes, process leaks on failures, and external provider flakiness. These tests are the main safety net for a provider with many moving external parts.
