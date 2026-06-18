# sources/security-integrity/cryfs/crates/cryfs-runner/src/ipc/mod.rs

## Purpose
Defines the internal IPC module composition and re-exports the types/functions needed by runner and integration tests.

## Important APIs, types, and functions
- Private modules: `pipe`, `rpc`, `spawn`.
- Public re-exports: `RpcClient`, `RpcConnection`, `RpcServer`, `rpc_server_from_inherited_fds`, `send_handshake`, `start_background_process`, and `start_background_process_with_exe`.

## Control flow
No runtime logic. It is a namespace boundary that keeps low-level pipe details private while exposing typed RPC and spawn entry points.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Used by `background_process.rs`, `lib.rs`, the test helper binary, and runner integration tests.

## Risks and edge cases
Re-exporting hidden test APIs from `lib.rs` means changes here can break integration tests. Keeping `pipe` private helps prevent callers from bypassing spawn/handshake invariants.

## Test signals
Compile-time linkage of daemon tests and background process code is the relevant signal.
