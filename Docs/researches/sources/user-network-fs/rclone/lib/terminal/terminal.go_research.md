# sources/user-network-fs/rclone/lib/terminal/terminal.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal.go -->
## sources/user-network-fs/rclone/lib/terminal/terminal.go

Purpose: central terminal utility package defining VT100 escape constants and selecting an output writer that supports or strips color appropriately.

Important APIs and control flow: constants define erase/move/title/color/style escape sequences. `Start()` runs once, reads global config, checks whether stdout is a terminal, and selects `Out` as either raw stdout, `colorable.NewColorable`, or `colorable.NewNonColorable` depending on platform, `TERM`, and `TerminalColorMode`. `WriteString` and `Write` lazily initialize and write to `Out`. `EnableColorsStdout()` asks colorable to enable native Windows VT support.

State, dependencies, and integration: package state is `once` and `Out io.Writer`. It depends on `os`, `runtime`, `sync`, `context`, `go-colorable`, and rclone `fs`. Build-specific files provide `IsTerminal` and related helpers. It integrates with progress/status output throughout rclone.

Risks and test signals: because `Start` is guarded by `sync.Once`, later config changes will not affect `Out`. Writes ignore write errors. No tests in this subset cover color mode or terminal detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/terminal.go -->
