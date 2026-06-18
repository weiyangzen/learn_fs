<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_shutdown.go -->
# sources/sync-backup/kopia/cli/command_server_shutdown.go

Purpose: implements `server shutdown`, requesting graceful shutdown of a running Kopia server.

Important APIs/types/functions: `commandServerShutdown`, `serverClientFlags`, `textOutput`, `apiclient.KopiaAPIClient`, `serverapi.Empty`, and endpoint `control/shutdown`.

Control flow: setup registers server client flags and output, then uses a server action. `run` posts an empty request to the shutdown endpoint.

State/persistence behavior: local CLI is stateless; server-side state transitions toward shutdown and should stop accepting later control requests.

Dependencies/integration: depends on server control API and graceful shutdown implementation in the server process. Risks/test signals: the command returns after the POST succeeds, while the server may still need time to exit; tests wait on server process completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_shutdown.go -->
