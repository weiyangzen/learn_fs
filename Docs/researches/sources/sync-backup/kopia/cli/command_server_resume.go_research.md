<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_resume.go -->
# sources/sync-backup/kopia/cli/command_server_resume.go

Purpose: implements `server resume` with alias `unpause`, resuming scheduled snapshots for matching sources.

Important APIs/types/functions: `commandServerResume`, embedded `commandServerSourceManagerAction`, `run`, and endpoint `control/resume-source`.

Control flow: setup registers the command alias, source/all flags, server client options, and a server action. `run` delegates to the shared source-manager action helper.

State/persistence behavior: local CLI is stateless; matched server-managed source state is resumed server-side.

Dependencies/integration: depends on server source manager and authenticated control API. Risks/test signals: shares the same source matching constraints and response logging behavior as pause/snapshot/cancel.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_resume.go -->
