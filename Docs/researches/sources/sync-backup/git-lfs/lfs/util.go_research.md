# sources/sync-backup/git-lfs/lfs/util.go

Purpose: Supplies platform detection, progress callback logging, path conversion, and file copy/link/temp helpers for LFS file operations.

Important APIs/types/functions: `Platform`, `GetPlatform`, `PathConverter`, `NewCurrentToRepoPathConverter`, `NewCurrentToRepoPatternConverter`, `CopyCallbackFile`, `CopyFileContents`, `LinkOrCopy`, and `TempFile`.

Control flow: `CopyCallbackFile` checks `GIT_LFS_PROGRESS`, validates absolute path, creates the directory, opens the log in append mode, and returns a throttled `tools.CopyCallback`. Path converters compute current working directory relative to repo root and optionally append slash or normalize `./` patterns.

State and persistence behavior: `currentPlatform` caches runtime OS. Progress logging appends to an external file and syncs each emitted line. `CopyFileContents` writes through a temp file in the configured temp directory and renames atomically. `LinkOrCopy` tries hard-linking before copy fallback.

Dependencies and integration points: Depends on `config.Configuration`, `tools` file helpers, `tasklog.DefaultLoggingThrottle`, `clock` through `GitFilter`, and OS filesystem semantics.

Risks and edge cases: Progress logging silently disables when env/event/filename is empty but errors on relative progress paths. `CopyFileContents` may fail cross-device rename if temp dir is not on the destination filesystem. Path conversion relies on symlink resolution and current process cwd.

Test signals: `util_test.go` covers callback read accounting and progress throttling. Path conversion and copy/link behavior are not directly covered here.
