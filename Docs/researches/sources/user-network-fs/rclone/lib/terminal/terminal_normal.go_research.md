# sources/user-network-fs/rclone/lib/terminal/terminal_normal.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_normal.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal_normal.go

Purpose: non-JavaScript terminal operations backed by `golang.org/x/term`.

Important APIs and control flow: `GetSize()` calls `term.GetSize` on stdout and falls back to `80x25` on error. `IsTerminal(fd)` delegates to `term.IsTerminal`. `ReadPassword(fd)` delegates to `term.ReadPassword`. `WriteTerminalTitle(title)` writes the VT100 title sequence to stdout.

State, dependencies, and integration: no persistent state. Dependencies are `fmt`, `os`, and `x/term`. It integrates with terminal UI sizing, password prompts, and title updates.

Risks and test signals: terminal title output writes directly to stdout, not `terminal.Out`. Password reading and terminal sizing are environment-dependent. No tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal_normal.go -->
