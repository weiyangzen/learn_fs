<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_disconnect.go -->
# sources/sync-backup/kopia/cli/command_repository_disconnect.go

Purpose: implements `repository disconnect`, removing the local repository configuration.

Important APIs/types/functions: `commandRepositoryDisconnect`, `setup`, `run`, `svc.noRepositoryAction`, and `repo.Disconnect`.

Control flow: setup creates the command under advanced services and uses a no-repository action, meaning it does not require successfully opening the configured repository. `run` calls `repo.Disconnect` on the configured repository config file path and logs completion.

State/persistence behavior: removes or invalidates the local connection config; it does not delete repository data from blob storage.

Dependencies/integration: depends on repository config file naming and disconnect semantics in the repo package. Risks/test signals: because no repository open is required, disconnect can clean up broken or inaccessible local configs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_disconnect.go -->
