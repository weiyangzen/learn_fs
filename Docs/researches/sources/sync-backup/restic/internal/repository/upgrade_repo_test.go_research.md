
# sources/sync-backup/restic/internal/repository/upgrade_repo_test.go

Purpose: tests repository config upgrade success and failure recovery.

`TestUpgradeRepoV2` creates a version 1 repository and verifies `UpgradeRepo` succeeds. `failBackend` wraps a backend and fails config-file saves after a configurable number of successful saves. `TestUpgradeRepoV2Failure` uses that wrapper so the initial repository creation succeeds but upgrade and rollback save fail, then asserts an `upgradeRepoV2Error` contains upload error, reupload error, and backup path. The test removes the backup file and directory afterward.

State is backend config persistence plus local temporary backup files. Integration points include `UpgradeRepo`, backend `Save`, raw config loading, config backup, and error wrapping. Risks covered include failure after removing/replacing config, missing backup reporting, and rollback errors being preserved for the caller.
