# sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go

Purpose: JavaScript/unsupported terminal implementation.

Important APIs and control flow: `GetSize()` returns `80x25`; `IsTerminal` always false; `ReadPassword` returns an error; `WriteTerminalTitle` is a no-op.

State, dependencies, and integration: no state. It imports `errors` only. Build tags keep terminal-dependent code compiling on JS targets.

Risks and test signals: password prompts cannot work on this target through this API. No tests are present in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_unsupported.go -->
