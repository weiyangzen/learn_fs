<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_status.go -->
# sources/sync-backup/kopia/cli/command_repository_status.go

Purpose: implements `repository status`, displaying local client options, storage information, content/object format, epoch/retention/upgrade state, required features, and optional reconnect tokens.

Important APIs/types/functions: `commandRepositoryStatus`, `RepositoryStatus`, `outputJSON`, `dumpUpgradeStatus`, `dumpRetentionStatus`, `run`, `outputRequiredFeatures`, `scanCacheDir`, `scrubber.ScrubSensitiveData`, and `dr.Token`.

Control flow: setup registers reconnect-token flags and JSON output. Text mode prints config path, client options, storage type/capacity/config, unique ID, hash/encryption/splitter, format version, content compression, password-change support, required features, pack/index settings, epoch manager details, retention, and upgrade lock status. Token mode optionally includes password and prints a reconnect command.

State/persistence behavior: read-only, except it may request the password to include in a reconnect token. JSON mode scrubs sensitive storage config before output.

Dependencies/integration: integrates direct repository introspection, blob volume capacity, format manager, epoch manager, upgrade lock intent, and output scrubbing. Risks/test signals: reconnect tokens with password are explicitly sensitive and trivially decodable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_status.go -->
