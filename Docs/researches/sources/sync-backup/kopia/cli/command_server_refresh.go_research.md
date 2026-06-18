<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_refresh.go -->
# sources/sync-backup/kopia/cli/command_server_refresh.go

Purpose: implements `server refresh`, asking a running server to refresh its source/cache view.

Important APIs/types/functions: `commandServerRefresh`, `serverClientFlags`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/refresh`.

Control flow: setup registers server client flags and a server action. `run` posts an empty request to `control/refresh` and expects an empty response.

State/persistence behavior: local CLI is stateless; server may rescan repository manifests or source definitions and update in-memory state.

Dependencies/integration: used when snapshots are created outside the server and the server must observe them. Risks/test signals: no polling occurs here; callers/tests must wait for refreshed state to appear in `server status`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_refresh.go -->
