# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/spawn.rs

## Purpose
Spawns the background daemon via fork+exec, maps RPC fds into conventional child slots, validates daemon identity with a build-id handshake, and reconstructs daemon-side RPC from inherited fds.

## Important APIs, types, and functions
- Constants define child fds 3/4, hidden `--daemon`, and 10-second handshake timeout.
- `daemon_exe_path` uses `/proc/self/exe` on Linux and `current_exe` elsewhere.
- `start_background_process` starts the production daemon and validates handshake.
- `start_background_process_with_exe` starts a test helper without the build-id handshake.
- `start_background_process_inner` performs fd mapping through `command-fds`.
- `validate_handshake_and_build_client`, `send_handshake`, and `rpc_server_from_inherited_fds` enforce identity and fd sanity.

## Control flow
Production spawn rejects running under an active tokio runtime, resolves the executable, creates RPC pipes, maps child request-recv and response-send fds to 3/4, spawns, then waits for a raw daemon-to-parent build-id handshake before returning the typed client. Daemon-side startup first validates fds are pipes and later sends its build id. Test helper spawn uses the same fd mapping but skips the production handshake.

## State and persistence behavior
State is process identity, environment, argv, and inherited pipe descriptors. No persistent disk state is written here.

## Dependencies and integration points
Uses `command-fds`, Unix `CommandExt::arg0`, `libc::fstat`, `RpcConnection`, `RpcClient`, `RpcServer`, `crate::build_id`, and serde. Production entry is called by `BackgroundProcess::daemonize`; daemon entry is called by `run_as_background_daemon`.

## Risks and edge cases
The pre-exec fd mapping path inherits known fork-after-multithread hazards; the runtime guard reduces risk. Non-Linux `current_exe` can re-resolve a replaced binary, so the build-id handshake covers but cannot pin the exact inode. `start_background_process_with_exe` deliberately skips handshake for tests and must not be used as production identity validation.

## Test signals
Unit tests accept matching build ids and reject mismatched, non-UTF8, EOF-before-handshake, and hung-without-handshake cases. Integration tests cover fd isolation and daemon survival after parent exit.
