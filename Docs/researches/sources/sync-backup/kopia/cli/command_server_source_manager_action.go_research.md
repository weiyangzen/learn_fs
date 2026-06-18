<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_source_manager_action.go -->
# sources/sync-backup/kopia/cli/command_server_source_manager_action.go

Purpose: shared helper for server commands that act on one source or all sources managed by the server, used by snapshot/upload, cancel, pause, and resume.

Important APIs/types/functions: `commandServerSourceManagerAction`, `setup`, `triggerActionOnMatchingSources`, `serverClientFlags`, `serverapi.MultipleSourceActionResponse`, `url.Values`, and `filepath.Abs`.

Control flow: setup registers `--all`, optional source argument, server client flags, and output. `triggerActionOnMatchingSources` rejects calls without `--all` or source, converts source to an absolute path, sends a POST to the supplied endpoint with optional `path` query parameter, and logs success or failure for each source in the response.

State/persistence behavior: local helper is stateless; all mutations happen in server-side control endpoints. It normalizes source paths before sending them.

Dependencies/integration: shared by several server control commands and therefore centralizes source matching semantics. Risks/test signals: response failures per source are logged as warnings but do not become command errors unless the API request itself fails.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_source_manager_action.go -->
