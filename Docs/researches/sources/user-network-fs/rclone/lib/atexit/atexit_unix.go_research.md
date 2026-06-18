
# sources/user-network-fs/rclone/lib/atexit/atexit_unix.go

Purpose: Unix platform signal list and exit-code conversion for `atexit`.

Important APIs/types/functions: build tag excludes Windows/Plan 9. `exitSignals` handles `SIGINT` and `SIGTERM`, intentionally not `SIGQUIT`. `exitCode` returns `128+signum` for real positive `syscall.Signal`, else uncategorized.

Control flow: used by signal goroutine in `atexit.Register`.

State/persistence: no mutable state here.

Dependencies/integration: imports `os`, `syscall`, and `exitcode`.

Risks: only selected signals trigger cleanup; unhandled fatal signals and SIGQUIT use default behavior.

Test signals: covered by `TestExitCode` on Unix-like systems.
