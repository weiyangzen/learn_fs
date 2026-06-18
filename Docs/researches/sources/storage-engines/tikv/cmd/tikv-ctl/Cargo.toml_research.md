# sources/storage-engines/tikv/cmd/tikv-ctl/Cargo.toml

## Purpose
This manifest defines the `tikv-ctl` command crate, its feature forwarding, operational dependencies, and shared build script dependencies.

## Important APIs, types, and functions
The package is `tikv-ctl` version `0.0.1`, edition 2024, unpublished. Features forward allocator, RocksDB portability/SSE, memory profiling, failpoints, vendored OpenSSL, and test engine choices to the root `tikv` crate or engine crates. `nortcheck` forwards to `engine_rocks/nortcheck`.

Dependencies include clap/structopt for CLI parsing, TiKV engine/storage/security/PD/raft crates, `raft-engine-ctl`, `compact-log-backup`, protobuf, grpcio, logging, base64/hex/regex/toml/tempfile, and tokio. Build dependencies are `cc` and workspace `time`.

## Control flow
Cargo uses this manifest to compile `tikv-ctl`. Feature selections from the root Makefile or Cargo invocation propagate into this crate and its dependencies. The build script includes shared command build logic.

## State and persistence behavior
No runtime state is defined here, but dependencies enable `tikv-ctl` to inspect and mutate local/remote TiKV state, RocksDB data, raft logs, encryption metadata, and backup logs.

## Dependencies and integration points
It is a default workspace member and release binary target. It integrates with TiKV's root package, workspace dependencies, Makefile `ctl`/release targets, and operational components for recovery, compaction, metrics, encryption, and raft-engine control.

## Risks and edge cases
Edition 2024 can impose newer compiler requirements than the root edition 2021. Feature forwarding must stay aligned with root features. Because the binary exposes destructive recovery/compaction operations, dependency version and feature drift can affect operational safety.

## Test signals
`cargo build -p tikv-ctl`, `make ctl`, feature-specific builds, CLI help generation, and command parser tests from `cmd.rs` are the main validation signals.
