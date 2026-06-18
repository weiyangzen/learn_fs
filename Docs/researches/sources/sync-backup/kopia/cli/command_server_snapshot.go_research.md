<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_snapshot.go -->
# sources/sync-backup/kopia/cli/command_server_snapshot.go

Purpose: implements `server snapshot` with alias `upload`, triggering snapshots for matching server-managed sources.

Important APIs/types/functions: `commandServerUpload`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/trigger-snapshot`.

Control flow: setup registers command aliases, source/all flags, server client options, and a server action. `run` delegates to the shared source-manager action helper for POST construction, response handling, and success/failure logging.

State/persistence behavior: local CLI is stateless; server-side action queues or starts snapshot uploads that create repository snapshot manifests and content.

Dependencies/integration: integrates server authentication, source manager, scheduler/upload pipeline, and notification behavior. Risks/test signals: triggering all sources can start multiple uploads; command success only reflects server acceptance/response per source, not necessarily long-term repository health.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_snapshot.go -->
