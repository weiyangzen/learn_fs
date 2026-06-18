<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_client.go -->
# sources/sync-backup/kopia/cli/command_repository_set_client.go

Purpose: implements `repository set-client`, mutating local client options stored in the repository config file.

Important APIs/types/functions: `commandRepositorySetClient`, `rep.ClientOptions`, `repo.SetClientOptions`, read-only/read-write flags, description/username/hostname list flags, permissive cache loading, and format-blob cache flags.

Control flow: setup registers client option flags and uses a repository-reader action. `run` copies current client options, applies requested changes, rejects no-op invocations, and persists the changed options to the local config file.

State/persistence behavior: updates local config only; repository storage and format parameters are not changed. Read-only mode, user/host identity, description, permissive cache loading, and format cache duration affect future opens.

Dependencies/integration: integrates app config path services and repo config persistence. Risks/test signals: the permissive cache loading branch appears inverted in its condition/logging, so setting it when currently false logs that the repository fails on bad index blobs without enabling the option.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_client.go -->
