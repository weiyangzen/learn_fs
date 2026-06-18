<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_pause.go -->
# sources/sync-backup/kopia/cli/command_server_pause.go

Purpose: implements `server pause`, pausing scheduled snapshots for matching server-managed sources.

Important APIs/types/functions: `commandServerPause`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/pause-source`.

Control flow: setup registers source/all flags and server client options, then wires a server action. `run` delegates source matching and POST handling to `triggerActionOnMatchingSources`.

State/persistence behavior: local CLI is stateless; server-side source state is marked paused for matched sources.

Dependencies/integration: depends on source manager control API and path matching. Risks/test signals: source paths are normalized to absolute paths unless `--all` is used, so relative-path expectations must account for the client's cwd.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_pause.go -->
