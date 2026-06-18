# sources/sync-backup/kopia/internal/ospath/ospath.go

Purpose: centralizes user-visible path and directory resolution across platforms.

Important APIs/types/functions: package variables for `homeDir`, `configDir`, and `logsDir`; `ConfigDir`, `LogsDir`, `IsAbs`, and `ResolveUserFriendlyPath`.

Control flow: `ConfigDir` and `LogsDir` return platform-initialized directories. `IsAbs` expands leading `~` first then delegates to `filepath.IsAbs`. `ResolveUserFriendlyPath` expands `~`, optionally makes relative paths home-relative, and cleans the result.

State and persistence behavior: package-level variables are initialized by OS-specific `init` files and environment lookups; no files are written here.

Dependencies and integration points: server path APIs, config discovery, log placement, and CLI path handling call into this package.

Risks and test signals: environment-dependent init paths can vary by OS and CI setup. Tests cover absolute-path behavior, but additional checks should cover tilde expansion and relative-to-home behavior.
