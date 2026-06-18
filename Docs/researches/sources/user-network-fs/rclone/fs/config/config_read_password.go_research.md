# sources/user-network-fs/rclone/fs/config/config_read_password.go

Purpose: provides terminal-aware password input for supported OSes.

Important APIs/functions: `ReadPassword() string`, built under `!plan9`.

Control flow: obtains stdin file descriptor, falls back to `ReadLine("")` when stdin is not a terminal, otherwise calls `terminal.ReadPassword`, prints a newline to stderr, fatals on read error, and returns the password bytes as a string.

State and persistence behavior: no persistence. It reads from process stdin and writes a newline to stderr to restore prompt layout.

Dependencies and integration points: depends on `terminal.IsTerminal`, `terminal.ReadPassword`, `fs.Fatalf`, and the UI `ReadLine` fallback. Used by config password prompts in `crypt.go`/`ui.go`.

Risks: fatal-on-read-error exits the process. Non-terminal input echoes through `ReadLine`, which is appropriate for pipes but less secure than terminal password mode.

Test signals: no direct test in this subset; password behavior is indirectly exercised through crypt/UI tests with mocked input elsewhere.
