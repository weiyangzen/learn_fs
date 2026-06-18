# sources/security-integrity/cryfs/crates/cryfs-runner/src/lib.rs

## Purpose
Public root of the `cryfs-runner` crate, exporting mounting APIs, hidden integration-test IPC APIs, daemon entry point, build identity, and tokio runtime initialization.

## Important APIs, types, and functions
- Re-exports `AtimeUpdateBehavior`, `Mounter`, `CreateOrLoad`, `FuseOption`, `MountArgs`, and `make_device`.
- Hidden exports expose `RpcClient`, `RpcServer`, spawn helpers, and inherited-fd reconstruction for integration tests.
- `BUILD_ID` and `build_id` derive a compile-time `VersionInfo`.
- `run_as_background_daemon` reconstructs server fds, calls `setsid`, sends handshake, and enters background main.
- `init_tokio` builds the multi-threaded runtime.

## Control flow
Production CLI dispatches to `run_as_background_daemon` for the hidden daemon flag. The daemon validates inherited fds, creates a new session, sends build-id bytes to the parent, then hands the server to `background_process::background_main`, which initializes tokio.

## State and persistence behavior
No filesystem persistence is performed here. Runtime state includes inherited fds, process session, build id, and the tokio runtime. Version assertion is compile-time.

## Dependencies and integration points
Connects `background_process`, `ipc`, `mounter`, `runner`, `unmount_trigger`, `cryfs-version`, `libc::setsid`, and `cryfs_cli_utils`-initialized CLI dispatch.

## Risks and edge cases
`setsid` failure is fatal because daemon detachment depends on it. Startup errors exit with distinct codes. Hidden IPC exports are not stable API but are visible to tests. `init_tokio` unwraps runtime construction.

## Test signals
Integration tests indirectly validate `setsid`, fd reconstruction, build-id handshake compatibility, and hidden IPC exports. Compile-time version assertions also guard package/git consistency.
