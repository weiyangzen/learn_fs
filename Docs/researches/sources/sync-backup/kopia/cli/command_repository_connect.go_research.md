<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect.go -->
# sources/sync-backup/kopia/cli/command_repository_connect.go

Purpose: implements `repository connect` for storage providers and shared connection options used by both connect and create.

Important APIs/types/functions: `commandRepositoryConnect`, `connectOptions`, `toRepoConnectOptions`, `getFormatBlobCacheDuration`, `App.runConnectCommandWithStorage`, `App.runConnectCommandWithStorageAndPassword`, `repo.Connect`, and `passwordpersist.OnSuccess`.

Control flow: setup registers shared cache/client flags, API-server connect subcommand, and one storage-provider subcommand per registered provider. Provider actions connect to blob storage, prompt/read password, then call repo connect. Connection options include cache directory/sizes, host/user override, read-only, permissive cache loading, description, action enablement, update checks, and format-blob cache control.

State/persistence behavior: writes or updates the local repository config file and persists the password only after successful `repo.Connect`. It does not initialize repository storage.

Dependencies/integration: depends on storage provider flags, password services, content cache settings, repo config, and update-check initialization. Risks/test signals: permissive cache loading is only meaningful for read-only repositories but this layer records the option without enforcing that relationship.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_connect.go -->
