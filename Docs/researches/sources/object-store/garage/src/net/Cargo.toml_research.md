# sources/object-store/garage/src/net/Cargo.toml

## Purpose
This manifest defines the `garage_net` crate, Garage's RPC networking library forked from Netapp. It configures package metadata, the library root, optional telemetry, dependencies, dev dependencies, and workspace lints.

## Important APIs, types, and functions
The crate is named `garage_net` version `2.3.0`, with library path `lib.rs`. Feature `telemetry` enables `opentelemetry` and `opentelemetry-contrib`; default features are empty. Dependencies cover async runtime/streams (`tokio`, `tokio-util`, `tokio-stream`, `futures`), serialization (`serde`, `rmp-serde`), crypto/authenticated transport (`sodiumoxide`, `kuska-handshake`), byte buffers, sockets, logging, `arc-swap`, `thiserror`, `rand`, and config helpers.

## Control flow
Cargo uses this manifest to compile the network crate. Feature selection controls whether request telemetry propagation code in `client.rs` is compiled.

## State and persistence behavior
No runtime state. Dependency versions are inherited from the workspace, making the root workspace lock/configuration authoritative.

## Dependencies and integration points
Other Garage crates depend on `garage_net` for `NetApp`, endpoints, messages, priorities, peering, and errors. The manifest integrates with workspace lints and shared dependency versions.

## Risks and edge cases
Because dependencies are workspace-pinned, changes outside this crate can alter network behavior. The optional telemetry feature changes request encoding by adding telemetry IDs but should remain wire-compatible because request headers include a telemetry ID length. Edition is 2018, so syntax choices must remain compatible.

## Test signals
`net/test.rs` is compiled as the crate test module. Manifest-level signals include building with default features and with `--features telemetry`.
