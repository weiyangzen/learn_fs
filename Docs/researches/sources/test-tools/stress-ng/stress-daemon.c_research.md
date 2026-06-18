# sources/test-tools/stress-ng/stress-daemon.c

## Purpose
This stressor repeatedly creates daemonized child processes to exercise `fork()`, `setsid()`, signal reset, environment clearing, descriptor rebinding, process reaping, capability dropping, and init/system reparenting behavior.

## Important APIs, Types, And Functions
`daemon_wait_pid()` optionally waits for a child when `daemon-wait` is enabled. `stress_make_daemon()` runs inside the first child, calls `setsid()`, closes standard descriptors, resets signals, clears the signal mask and optional environment, opens `/dev/null` as fds 0/1/2, then repeatedly forks daemon children. `stress_daemon()` owns the parent pipe, initial fork, result reads, bogo increments, and cleanup. `stress_daemon_info` exposes `daemon-wait`.

## Control Flow
The top-level worker disables `SIGALRM` stress-stop behavior, creates a pipe, synchronizes, and forks. The child closes the read side and calls `stress_make_daemon()`. That routine reports setup failures through the pipe before stdio closure, then the daemon child changes directory to `/`, clears umask, drops capabilities, marks run state, and writes success to the pipe. The original parent reads result codes, increments bogo count for successes, and either waits for the intermediate child or lets init reap descendants depending on `daemon-wait`.

## State And Persistence
The stressor intentionally manipulates process/session state but does not persist files. It may leave daemon children to be reaped by init when `daemon-wait` is false, by design. All communication to the original parent is through the pipe before descriptor cleanup.

## Dependencies And Integration Points
Dependencies include stress-ng signal helpers, capability dropping, fork retry helpers, process state APIs, `/dev/null`, optional `clearenv()`, and option parsing through `OPT_daemon_wait`. It is classified as scheduler and OS work.

## Risks
Fork pressure can hit pid or memory limits. Because stdout/stderr are intentionally closed in the daemon path, many later setup failures cannot be reported directly and are silently retried or cleaned up. Signal reset loops iterate over `MAX_SIGNUM`, which is platform-dependent. Incorrect `daemon-wait` use changes whether the stressor waits directly or relies on init reaping.

## Test Signals
Signals include successful bogo increments for daemon creations, no fd leaks around `/dev/null`, no zombie buildup when `daemon-wait` is enabled, acceptable init reaping when disabled, and graceful retry/backoff on `EAGAIN` or `ENOMEM` fork failures.
