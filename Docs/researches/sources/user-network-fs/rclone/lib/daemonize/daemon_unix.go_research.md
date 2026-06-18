# sources/user-network-fs/rclone/lib/daemonize/daemon_unix.go

## Purpose
This Unix implementation starts a background twin of the current rclone process and provides a non-blocking health check for the child. It is designed to emulate daemonization without unsafe `fork` in a Go process with goroutines.

## Important APIs, types, and functions
- Build constraint: `unix && !aix`.
- `StartDaemon(args []string) (*os.Process, error)` starts the child process or returns nil in a process already marked daemonized.
- `argsToEnv(origArgs, origEnv []string) (args, env []string)` converts mount-helper style `--flag` and `--flag=value` options to `RCLONE_*` environment variables.
- `Check(daemon *os.Process) error` uses `unix.Wait4(..., WNOHANG, ...)` to detect child exit.

## Control flow
`StartDaemon` first checks `fs.IsDaemon` to avoid spawning again. It marks the child via `fs.DaemonMarkVar=fs.DaemonMarkChild`, resolves the executable path, replaces `args[0]` with that path when args are provided, optionally moves flags into environment variables, opens `/dev/null` for stdin/stdout/stderr, and starts a process with `Setsid: false`. `Check` performs a non-blocking wait: no exited child returns nil, an exited child returns an error with its exit code, and wait errors are propagated.

## State and persistence behavior
State is external process state plus environment variables passed to the child. No files are persisted. The child has standard streams redirected to `/dev/null`.

## Dependencies and integration points
The file depends on `github.com/rclone/rclone/fs` for daemon markers and argument-passing policy, and `golang.org/x/sys/unix` for wait status. It integrates with mount helpers and command flows that need to background rclone while preserving processed options.

## Risks and edge cases
`StartDaemon` mutates the provided `args` slice by replacing element zero. The `/dev/null` file is not explicitly closed after `StartProcess`. `Setsid` is deliberately false for autofs process-group expectations, so this is not classic full daemon detachment. `argsToEnv` only handles long flags and assumes no `--flag value` or short-flag forms. `Check` only reports normal exit status; signal termination returns nil unless represented differently by wait status handling.

## Test signals
No tests in this subset exercise daemon spawning. Behavior is platform-sensitive and would need Unix integration tests around environment conversion, process lifecycle, and mount-helper expectations.
