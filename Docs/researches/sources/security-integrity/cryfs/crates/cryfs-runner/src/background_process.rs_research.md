# sources/security-integrity/cryfs/crates/cryfs-runner/src/background_process.rs

## Purpose
Implements parent-side background daemon control and daemon-side RPC serving for bootstrap, status, and mount requests.

## Important APIs, types, and functions
- `BackgroundProcess::daemonize` starts the daemon, sends bootstrap logging config, and performs a status check.
- `mount_filesystem` sends a `MountRequest` and maps serialized mount errors back to `CliError`.
- RPC schema: `BootstrapConfig`, `Request::{Bootstrap, StatusCheckRequest, MountRequest}`, and `Response::{BootstrapAck, StatusCheckResponse, MountResponse}`.
- `background_main` creates the tokio runtime; `background_async_main` enforces bootstrap-first protocol and serves requests.
- `handle_bootstrap` is a testable receive/install/ack helper; `close_stdout_stderr` redirects fd 0/1/2 to `/dev/null`.

## Control flow
The parent starts IPC, sends `Bootstrap`, waits up to 10 seconds for `BootstrapAck`, then sends `StatusCheckRequest`. The daemon requires `Bootstrap` as the first typed request, initializes logging through the callback, and only then acks. On mount, the daemon calls the runner; success callback sends `MountResponse(Ok(()))` immediately after mount succeeds and then detaches stdio while the mount loop continues until unmount.

## State and persistence behavior
State is in the live `RpcClient`/`RpcServer` pipes and serialized `MountArgs`. No disk state is created here except whatever logging destination the bootstrap config selects. Mounting persists through lower block/blob/filesystem layers.

## Dependencies and integration points
Uses `clap-logflag`, `cryfs_cli_utils::CliError`, serde, `anyhow`, runner mount logic, and the IPC spawn/rpc layer. `Mounter::run_in_background` wraps this type.

## Risks and edge cases
Unexpected response variants panic. Once a mount succeeds, the parent receives success before the filesystem later unmounts, so later mount errors may only be logged. Duplicate bootstrap is acked but ignored. If bootstrap logging fails, no ack is sent by design; parent sees a timeout/EOF-style startup failure.

## Test signals
In-file tests cover postcard serialization of logging config, bootstrap round trip over real pipes, no ack when logging install fails, and rejection of non-bootstrap first requests.
