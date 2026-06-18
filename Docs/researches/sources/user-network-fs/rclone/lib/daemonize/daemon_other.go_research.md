# sources/user-network-fs/rclone/lib/daemonize/daemon_other.go

## Purpose
This build-tagged file provides the daemonize API stub for platforms where rclone does not support daemon mode: non-Unix platforms and AIX.

## Important APIs, types, and functions
- Build constraint: `!unix || aix`.
- `errNotSupported` reports that daemon mode is unsupported on the current `runtime.GOOS`.
- `StartDaemon(args []string) (*os.Process, error)` always returns the unsupported error.
- `Check(daemon *os.Process) error` also always returns the unsupported error.

## Control flow
There is no branching beyond returning the package-level error. The exported function signatures match the Unix implementation.

## State and persistence behavior
No daemon process is created and no state is persisted.

## Dependencies and integration points
It imports `fmt`, `os`, and `runtime`. It lets higher-level mount/daemon code compile uniformly while receiving a platform-specific unsupported error.

## Risks and edge cases
Callers must treat the returned error as expected unsupported behavior. Because `Check` ignores its argument, passing nil or a dead process makes no difference on these platforms.

## Test signals
No tests in this subset target the stub directly. Platform build coverage is the main signal.
