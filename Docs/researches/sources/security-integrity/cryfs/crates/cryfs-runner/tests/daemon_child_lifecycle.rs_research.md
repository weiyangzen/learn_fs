# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_child_lifecycle.rs

## Purpose
Integration tests for daemon child lifecycle behavior when the helper daemon echoes, panics, or exits before/after requests.

## Important APIs, types, and functions
- Defines matching `Request`/`Response` structs.
- `helper_exe` locates `cryfs-runner-test-background`.
- `spawn_daemon` passes `CRYFS_TEST_BEHAVIOR` and calls `start_background_process_with_exe`.
- Tests cover echo, panic after request, panic before request, exit after request, and exit before request.

## Control flow
Each test spawns a clean helper process through the same fork+exec/fd mapping path. Echo sends one request and expects incremented response. Failure modes either send a request then read or read immediately; each expects `recv_response` to fail with `Sender closed the pipe`.

## State and persistence behavior
No persistent state except helper process lifetime. Environment variables configure behavior for the spawned child.

## Dependencies and integration points
Exercises `cryfs_runner::start_background_process_with_exe`, `RpcClient`, postcard serialization, inherited fds, EOF propagation, and the helper binary.

## Risks and edge cases
The test intentionally avoids in-process fork of libtest threads, addressing previous fd-inheritance flakes. It depends on exact error string from pipe EOF handling.

## Test signals
Signals are successful request/response for echo and EOF errors for daemon panic/exit before or after a request.
