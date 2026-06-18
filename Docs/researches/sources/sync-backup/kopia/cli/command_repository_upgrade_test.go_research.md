<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade_test.go -->
# sources/sync-backup/kopia/cli/command_repository_upgrade_test.go

Purpose: format-specific integration and unit coverage for experimental repository upgrade behavior.

Important APIs/types/functions: `TestRepositoryUpgrade`, `TestRepositoryCorruptedUpgrade`, `TestRepositoryUpgradeCommitNever`, `TestRepositoryUpgradeCommitAlways`, `TestRepositoryUpgradeStatusWhileLocked`, `lockRepositoryForUpgrade`, and `TestRepositoryUpgrade_checkIndexInfo`.

Control flow: tests create repositories across format versions, enable the upgrade environment gate, run upgrade begin with short unsafe timing, verify format-version-specific messages and final status, leave locks with commit-mode never, corrupt migrated indexes to force validation failure, force always commit, inspect locked status as owner/non-owner, rollback locks, wait for drain, finalize upgrade, and unit-test each `CheckIndexInfo` mismatch field.

State/persistence behavior: mutates repository format, upgrade locks, and index blobs; one test intentionally corrupts repository files for validation coverage.

Dependencies/integration: spans filesystem storage, format versions, upgrade owner IDs, lock timing, index epoch status, and status command. Risks/test signals: `TestRepositoryUpgradeStatusWhileLocked` includes a real 62-second sleep for drain behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade_test.go -->
