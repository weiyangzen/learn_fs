# sources/storage-engines/tikv/components/pd_client/Cargo.toml

## Purpose
This manifest defines the private `pd_client` crate, TiKV's Placement Driver client abstraction and implementations.

## Important APIs, Types, and Functions
It declares `failpoints` and `testexport` features. Dependencies include `grpcio`, `kvproto`, `security`, `futures`, `tokio`, `tokio-timer`, `yatp`, `txn_types`, `prometheus`, `slog`, `semver`, and several workspace utility crates.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no state; the crate it defines maintains PD connections, streams, feature gates, and metrics.

## Dependencies and Integration Points
Dependencies show the crate's role: gRPC/protobuf communication with PD, security/TLS setup, async and legacy future interop, metrics, failpoints, and cluster-version feature gating.

## Risks
The crate sits on critical cluster-control paths. Feature flags expose failpoints and test-only APIs; enabling them incorrectly in production would be risky. Async dependency compatibility matters because this crate bridges futures 0.1, futures 0.3, Tokio, and grpcio.

## Test Signals
Tests are distributed across modules not all in this subset; manifests themselves are compile-time checked.
