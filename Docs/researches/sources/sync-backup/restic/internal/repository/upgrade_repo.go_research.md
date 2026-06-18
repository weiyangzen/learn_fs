
# sources/sync-backup/restic/internal/repository/upgrade_repo.go

Purpose: upgrades repository config from format version 1 to version 2, with a local config backup and rollback attempt on upload failure.

Important APIs are `UpgradeRepo`, internal `upgradeRepository`, and `upgradeRepoV2Error`. `UpgradeRepo` validates the repo is version 1, creates a temp dir, loads the raw config file, writes a backup file, then calls `upgradeRepository`. `upgradeRepository` removes the config first for backends without atomic replace, changes config version to 2, and saves it encrypted through `restic.SaveConfig`.

State and persistence include the backend config file and a local temporary backup. On failure, `UpgradeRepo` removes any partial config and attempts to reupload the original raw bytes; errors report both the new-upload failure and rollback failure plus backup path. Risks include non-atomic replace windows, rollback failure, temporary backup cleanup, and only supporting v1-to-v2 upgrades. Tests cover successful upgrade and injected config-save failure with backup path reporting.
