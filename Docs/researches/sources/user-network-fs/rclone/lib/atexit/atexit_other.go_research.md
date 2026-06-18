
# sources/user-network-fs/rclone/lib/atexit/atexit_other.go

Purpose: platform-specific signal settings for Windows and Plan 9.

Important APIs/types/functions: build tag `windows || plan9`; defines `exitSignals = []os.Signal{os.Interrupt}` and `exitCode` returning `exitcode.UncategorizedError`.

Control flow: consumed by `atexit.Register` when installing signal notifications and deciding process exit code.

State/persistence: none beyond package variables.

Dependencies/integration: imports `os` and rclone `lib/exitcode`.

Risks: unlike Unix, it does not encode signal number in exit status; this is intentional for platforms without the same convention.

Test signals: `TestExitCode` asserts this behavior on Windows/Plan 9.
