<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_from_config.go -->
# sources/sync-backup/kopia/cli/command_repository_connect_from_config.go

Purpose: storage provider implementation named `from-config`, allowing connect/create operations from a repository config file or encoded storage token.

Important APIs/types/functions: `storageFromConfigFlags`, `Setup`, `Connect`, `connectToStorageFromConfigFile`, `connectToStorageFromConfigToken`, `connectToStorageFromStorageConfigFile`, `connectToStorageFromStorageConfigStdin`, `repo.LoadConfigFromFile`, `repo.DecodeToken`, `repo.EncodeToken` counterpart, and `blob.NewStorage`.

Control flow: setup registers `--file`, `--token`, `--token-file`, and `--token-stdin`. For connect, `--file` loads an existing config with blob storage connection info. Token inputs decode connection info and an optional password, set the password service from the token when present, and open storage.

State/persistence behavior: this provider opens blob storage only; actual repo config creation is handled by connect/create callers. Tokens can carry the repository password into password flags.

Dependencies/integration: registered through `mustRegisterStorageProvider` in `init`. Risks/test signals: server-only connection files are rejected because this provider requires blob storage parameters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect_from_config.go -->
