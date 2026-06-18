<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters.go -->
# sources/sync-backup/kopia/cli/command_repository_set_parameters.go

Purpose: implements `repository set-parameters`, mutating repository-wide format parameters, blob retention config, epoch-manager settings, and test-only required features.

Important APIs/types/functions: `commandRepositorySetParameters`, `updateRepositoryParameters`, `updateEpochParameters`, `disableBlobRetention`, `addRemoveUpdateRequiredFeatures`, `FormatManager().SetParameters`, `maintenance.CheckExtendRetention`, and `ContentManager().PrepareUpgradeToIndexBlobManagerV1`.

Control flow: setup registers max pack size, index version, retention mode/period, `--upgrade`, epoch tuning flags, and hidden required-feature flags. `run` loads mutable parameters, blob config, and required features; applies requested changes; prevents index-format downgrade; validates retention against maintenance; migrates to epoch manager when needed; persists parameters and optionally writes a legacy-index poison blob.

State/persistence behavior: changes the repository format blob and may rewrite index state during epoch-manager upgrade. Blob retention settings are stored in blob storage configuration. Required features can block future clients that do not understand them.

Dependencies/integration: touches format, epoch, feature gating, maintenance retention, and content index migration. Risks/test signals: high blast radius; the command warns that other clients must disconnect and reconnect after updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters.go -->
