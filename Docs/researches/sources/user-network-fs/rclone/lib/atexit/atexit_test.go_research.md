
# sources/user-network-fs/rclone/lib/atexit/atexit_test.go

Purpose: tests platform-specific `exitCode` behavior.

Important APIs/types/functions: `fakeSignal` implements `os.Signal` without being a real syscall signal. `TestExitCode` checks Windows/Plan 9 return uncategorized errors, Unix returns `128+signal` for known signals, and fake signals return uncategorized.

Control flow: runtime OS switch selects expectations.

State/persistence: none.

Dependencies/integration: uses `runtime`, `os`, `exitcode`, and `testify/assert`.

Risks: assumes POSIX signal numbers for SIGINT and SIGKILL on Unix-like platforms, as noted in comments.

Test signals: direct coverage of `atexit_other.go` and `atexit_unix.go` exit-code helpers.
