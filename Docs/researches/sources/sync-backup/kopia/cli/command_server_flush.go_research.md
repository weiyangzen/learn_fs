<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_flush.go -->
# sources/sync-backup/kopia/cli/command_server_flush.go

Purpose: implements `server flush`, asking a running Kopia server to flush in-memory state to persistent storage.

Important APIs/types/functions: `commandServerFlush`, `serverClientFlags`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/flush`.

Control flow: setup registers the command, server client flags, and a server action. `run` performs a POST with empty request and response bodies to the control endpoint.

State/persistence behavior: local CLI is stateless; server-side flush may persist source manager state, caches, or other server-maintained data.

Dependencies/integration: depends on authenticated server control API. Risks/test signals: no response payload is inspected, so success is purely HTTP/API success.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_flush.go -->
