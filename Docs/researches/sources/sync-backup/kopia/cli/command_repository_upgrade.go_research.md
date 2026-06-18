<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade.go -->
# sources/sync-backup/kopia/cli/command_repository_upgrade.go

Purpose: hidden experimental repository format upgrade workflow, with explicit lock intent, client drain, epoch index migration, validation, commit, and rollback commands.

Important APIs/types/functions: `commandRepositoryUpgrade`, `setLockIntent`, `drainOrCommit`, `drainAllClients`, `upgrade`, `validateAction`, `commitUpgrade`, `forceRollbackAction`, `runPhase`, `ignoreErrorOnAlwaysCommit`, `CheckIndexInfo`, `loadIndexBlobs`, `format.UpgradeLockIntent`, and `ContentManager().PrepareUpgradeToIndexBlobManagerV1`.

Control flow: setup gates use on `KOPIA_UPGRADE_LOCK_ENABLED`, registers `begin`, `rollback`, and `validate`. `begin` chains phases: place lock intent, wait for drain or proceed, migrate indexes to epoch format when needed, compare old/new index blobs, and commit the upgrade unless test commit mode says never. Errors set a `skip` flag to stop subsequent phases.

State/persistence behavior: writes upgrade lock intent, may block non-owner clients, rewrites index metadata to V1/epoch format, updates mutable format parameters, commits or rolls back upgrade state, and cleans rollback backups through format manager.

Dependencies/integration: high-risk integration with repository clocks, format blob cache timings, owner IDs, index readers, and content managers. Risks/test signals: explicitly warns of corruption/data-loss risk; validation compares critical `content.Info` fields but stops at first mismatch per pair due switch structure.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_upgrade.go -->
