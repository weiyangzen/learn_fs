<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_server.go -->
# sources/sync-backup/kopia/cli/command_repository_connect_server.go

Purpose: implements `repository connect server`, connecting the local CLI to a Kopia API server instead of direct blob storage.

Important APIs/types/functions: `commandRepositoryConnectServer`, `repo.APIServerInfo`, `repo.ConnectAPIServer`, `connectOptions.toRepoConnectOptions`, `passwordpersist.OnSuccess`, and `repo.SupportedLocalCacheKeyDerivationAlgorithms`.

Control flow: setup registers required `--url`, optional server certificate fingerprint, and hidden local-cache key derivation algorithm. `run` trims trailing slashes from the base URL, lowercases the fingerprint, resolves default username/hostname for logging, obtains the password, connects to the API server, persists password on success, logs completion, and initializes update checks.

State/persistence behavior: writes local repository config for an API-server connection, not direct storage. Password persistence is tied to the server connection config file.

Dependencies/integration: integrates API client trust configuration, local cache key derivation, password prompting, and shared connect options. Risks/test signals: a missing or wrong certificate fingerprint affects TLS trust at connect/open time rather than during this file's option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_server.go -->
