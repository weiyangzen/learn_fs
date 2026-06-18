# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_survives_parent_exit.rs

## Purpose
Regression test proving a spawned daemon survives after the parent CLI-like process exits and has moved into a separate session with `setsid`.

## Important APIs, types, and functions
- Uses `fork`, `waitpid`, `getsid`, and signal cleanup through `nix`.
- `DaemonGuard` kills the daemon with SIGTERM/SIGKILL on drop.
- The helper runs `sentinel_loop`, writing PID and updating a sentinel file.

## Control flow
The test forks a sub-process that starts the helper daemon and exits immediately. The parent reaps that sub-process, waits for the daemon PID file, installs cleanup guard, compares daemon session id to test session id, waits for the sentinel file, and verifies its contents change after the parent exited.

## State and persistence behavior
Temporary PID and sentinel files are created under a temp directory. The daemon writes a tick counter every 50 ms until killed.

## Dependencies and integration points
Validates `start_background_process_with_exe` plus helper-side `setsid` behavior used to model production daemon detachment.

## Risks and edge cases
The test uses global environment variables, marked safe by being a single-test integration binary. It polls for parseable PID content to avoid races with partial file creation. Cleanup must handle init-parented detached processes.

## Test signals
Signals are clean sub-process exit, parseable daemon PID, distinct session ids, sentinel creation, and sentinel content changes within deadlines.
