# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_daemonize.c

## Summary
Implements interlocked daemonization for rumpuser services.

## Key Details
- Prevents concurrent daemonization with a static `isdaemonizing` flag.
- Uses `socketpair(PF_LOCAL, SOCK_STREAM)` so the parent can wait for the child to report initialization status without SIGPIPE concerns.
- Forks before rump initialization creates threads; the child calls `setsid`.
- Allows `RUMP_STDOUT` and `RUMP_STDERR` to redirect standard output/error before forking.
- `rumpuser_daemonize_done` redirects stdin, and by default stdout/stderr, to `/dev/null` on success.
- Sends the final initialization error code to the parent, which exits with that status.

## Notes
The implementation intentionally does not `chdir("/")`; callers must decide whether to change directories.
