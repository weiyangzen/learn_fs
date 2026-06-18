# sources/user-network-fs/rclone/lib/env/env.go

Source read signal: reviewed complete local file (46 lines, sha256 2e886bf3b2592875).

Purpose: Provides small environment helpers for shell-like path expansion and current user detection.

Important APIs/types/functions: Exports `ShellExpandHelp`, `ShellExpand`, and `CurrentUser`.

Control flow: `ShellExpand` expands a leading tilde with `go-homedir` when possible, then runs `os.ExpandEnv`. `CurrentUser` prefers `user.Current`, except when `$USER` is literally `$USER` for documentation generation, then falls back to `$USER` and `$LOGNAME`.

State and persistence behavior: Reads environment variables and OS user info only; no state is written.

Dependencies and integration points: Uses `os`, `os/user`, and `mitchellh/go-homedir`. Help text is embedded in command option descriptions that accept paths.

Risks and test signals: Tilde expansion is intentionally only leading-position. `user.Current` can fail in static/cross/container environments, so fallback ordering matters; env tests cover `~`, embedded `~`, and `${VAR}` expansion.
