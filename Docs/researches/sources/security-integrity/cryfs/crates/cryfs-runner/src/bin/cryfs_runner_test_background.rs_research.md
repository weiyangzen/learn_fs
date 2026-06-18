# sources/security-integrity/cryfs/crates/cryfs-runner/src/bin/cryfs_runner_test_background.rs

## Purpose
Test-only helper daemon spawned by `start_background_process_with_exe` integration tests. It rebuilds an `RpcServer` from inherited fds 3 and 4 and executes behavior selected by `CRYFS_TEST_BEHAVIOR`.

## Important APIs, types, and functions
- Local `Request { request: i32 }` and `Response { response: i32 }` match integration tests.
- `rpc_server_from_inherited_fds` reconstructs the typed server.
- Behaviors include `echo`, `panic_after_request`, `panic_before_request`, `exit_after_request`, `exit_before_request`, `write_to_fd_then_idle`, and `sentinel_loop`.

## Control flow
Normal `echo` loops receiving requests and responding with `request + 1` until EOF. Panic/exit modes simulate daemon failures before or after receiving a request. FD-isolation mode attempts to write to a provided fd, writes its PID, calls `setsid`, and idles. Sentinel mode drops RPC, writes PID, calls `setsid`, and repeatedly updates a sentinel file.

## State and persistence behavior
The helper writes temporary PID and sentinel files for tests. It does not mount filesystems or persist CryFS data.

## Dependencies and integration points
Used by runner integration tests through `CARGO_BIN_EXE_cryfs-runner-test-background`. It exercises inherited fd reconstruction, EOF behavior, `setsid`, and daemon cleanup logic.

## Risks and edge cases
Environment variable usage in tests must be isolated because process env is global. Infinite idle loops require external cleanup guards in tests. The helper intentionally bypasses the production build-id handshake.

## Test signals
Integration tests use this binary to verify echo round trips, EOF on daemon death, detached survival after parent exit, and absence of leaked parent fds.
