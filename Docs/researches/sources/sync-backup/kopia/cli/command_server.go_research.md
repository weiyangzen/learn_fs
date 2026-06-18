<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server.go -->
# sources/sync-backup/kopia/cli/command_server.go

Purpose: top-level server command registrar and common server-control flag definitions.

Important APIs/types/functions: `commandServer`, `serverFlags`, `serverClientFlags`, `serverAPIClientOptions`, `apiclient.Options`, and server subcommand fields for start, ACL, user, status, refresh, flush, shutdown, snapshot/upload, cancel, pause, resume, and throttle.

Control flow: `serverFlags.setup` registers server start/listen credentials. `serverClientFlags.setup` registers address, control credentials, backwards-compatible aliases, and trusted certificate fingerprint. `commandServer.setup` registers all server subcommands. `serverAPIClientOptions` validates address and returns API client options.

State/persistence behavior: none directly; it builds command options for server start/control paths. Credentials may come from environment variables.

Dependencies/integration: central integration point for HTTP API server CLI and `internal/apiclient`. Risks/test signals: default address and default control username shape all server-control commands; missing password is allowed at option construction and handled by server authentication.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server.go -->
