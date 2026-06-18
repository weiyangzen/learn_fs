<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_cancel.go -->
# sources/sync-backup/kopia/cli/command_server_cancel.go

Purpose: implements `server cancel`, cancelling in-progress uploads for server-managed snapshot sources.

Important APIs/types/functions: `commandServerCancel`, embedded `commandServerSourceManagerAction`, `runServerCancelUpload`, and API endpoint `control/cancel-snapshot`.

Control flow: setup registers the command, common source/all flags, server client flags, and a server action. The run method delegates to `triggerActionOnMatchingSources` with the cancel endpoint.

State/persistence behavior: sends a control API request to the running server; any state mutation occurs server-side by cancelling source-manager work.

Dependencies/integration: depends on server API authentication, source matching, and `MultipleSourceActionResponse` handling. Risks/test signals: cancel requires either `--all` or a source path; endpoint failures are wrapped as server errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_cancel.go -->
