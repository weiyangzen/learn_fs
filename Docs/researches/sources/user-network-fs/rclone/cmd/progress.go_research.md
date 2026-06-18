# sources/user-network-fs/rclone/cmd/progress.go

Purpose: implements terminal progress rendering for commands using rclone accounting stats.

Important APIs/state: constants for terminal escape codes, `startProgress`, package globals `statsInterval`, `statsUnit`, and `printProgress`.

Control flow: `startProgress` intercepts log output when logs are not redirected and replaces `operations.SyncPrintf` so stdout-producing helpers can coexist with progress. A ticker prints stats at the default or configured interval; the returned stop function closes the goroutine, resets handlers, restores `SyncPrintf`, and emits a final newline. `printProgress` locks `operations.StdoutMutex`, trims stats/log text, rewinds/erases previous lines using terminal escape sequences, clips lines to terminal width, and writes through `terminal.Write`.

State/persistence: process-local goroutine/ticker and terminal output state; no files. Dependencies include accounting/stats, terminal handling, and command global flags. Risks include terminal escape issues on non-TTY/redirected output, races during shutdown, and log interleaving. Test signal likely indirect through command progress behavior.
