# sources/sync-backup/kopia/internal/server/api_paths.go

Purpose: resolves user-friendly local paths for the UI.

Important APIs/types/functions: `handlePathResolve`.

Control flow: decodes/reads path input from the request, calls `ospath.ResolveUserFriendlyPath`, and returns the resolved path in a serverapi response.

State and persistence behavior: stateless path string transformation.

Dependencies and integration points: used by UI forms before local filesystem operations such as estimate or source creation.

Risks and test signals: behavior depends on server OS and home directory. Tests cover API request/response around common relative and tilde paths.
