# sources/sync-backup/kopia/internal/mount/mount_net_use.go

Purpose: Windows implementation that exposes a WebDAV server as a drive letter via `net use`.

Important APIs/types/functions: `Directory`, `netUse`, `netUseMount`, `netUseUnmount`, `isWindowsDrive`, `isValidWindowsDriveOrAsterisk`, and `netuseController`.

Control flow: validates drive letter or `*`, starts a local WebDAV controller, invokes `net use` to map the URL, parses localized output for an assigned drive when `*` was requested, and returns a controller that unmaps the drive before shutting down WebDAV.

State and persistence behavior: the persistent OS state is a Windows drive mapping; in-process state is the wrapped WebDAV controller and selected drive letter.

Dependencies and integration points: depends on `exec.CommandContext`, Windows `net use`, `DirectoryWebDAV`, and server mount API calls.

Risks and test signals: output parsing is heuristic and localized; failed `net use` must unmount WebDAV to avoid leaks. Tests should cover drive validation, `*` parsing, command failure cleanup, and unmount ordering with mocked command execution.
