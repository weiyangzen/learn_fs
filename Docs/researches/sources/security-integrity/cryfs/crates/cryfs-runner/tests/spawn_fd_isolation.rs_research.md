# sources/security-integrity/cryfs/crates/cryfs-runner/tests/spawn_fd_isolation.rs

## Purpose
Regression test ensuring unrelated parent file descriptors do not leak into the daemon across fork+exec.

## Important APIs, types, and functions
- Creates a sentinel pipe and sets `FD_CLOEXEC` on both ends.
- Passes the sentinel writer fd number through `CRYFS_TEST_LEAK_FD`.
- Spawns helper behavior `write_to_fd_then_idle`.
- `DaemonGuard` kills and reaps the direct child daemon.

## Control flow
After spawning the helper, the parent drops its sentinel writer. The helper attempts to write to the fd number before publishing its PID. The parent waits for the PID, gives the helper time to run, then performs a nonblocking read on the sentinel receiver. EOF is expected; data or WouldBlock means a writer leaked into the daemon.

## State and persistence behavior
Temporary PID file only. The sentinel pipe is transient OS state.

## Dependencies and integration points
Exercises `start_background_process_with_exe`, `FD_CLOEXEC`, fd mapping, helper daemon behavior, `interprocess` pipes, and libc fcntl/waitpid/kill.

## Risks and edge cases
The sentinel pipe is intentionally marked CLOEXEC to isolate spawn behavior. The helper idles forever, so cleanup guard correctness is required. Timing includes a short sleep after PID publication to allow the write attempt.

## Test signals
EOF on the sentinel receiver is the core signal. Any bytes or open-writer WouldBlock failure indicates fd leakage.
