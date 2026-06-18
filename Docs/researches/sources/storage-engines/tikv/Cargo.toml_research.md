# sources/storage-engines/tikv/Cargo.toml

## Purpose
The root `Cargo.toml` defines the TiKV library package, workspace membership, feature topology, dependency graph, crates.io patches, workspace dependency aliases, and build/test/release profiles.

## Important APIs, types, and functions
The package is `tikv` version `9.0.0-beta.2`, Rust edition 2021, unpublished. Key features select allocators (`tcmalloc`, `jemalloc`, `mimalloc`, `snmalloc`), RocksDB portability/SSE, memory profiling, failpoints, test exports, test engines, frame-pointer pprof, and vendored OpenSSL. The `[workspace]` uses resolver 2, includes command crates, components, fuzz crates, and tests, excludes selected component folders, and defaults to `cmd/tikv-server` and `cmd/tikv-ctl`.

Dependencies span TiKV internal workspace crates for engines, raftstore, PD, security, resource control, backup, SQL coprocessor components, and utility crates, plus external crates for async, gRPC, protobuf, metrics, HTTP, crypto, serialization, and profiling. `[patch.crates-io]` redirects several crates to TiKV/PingCAP forks or local patches. Profiles tune compile speed and release size/performance.

## Control flow
Cargo uses this manifest to resolve feature propagation and workspace builds. Resolver 2 is explicitly required so features requested at the root propagate to command-crate direct dependencies as intended. Build behavior is further shaped by Makefile-provided features and environment variables.

## State and persistence behavior
The manifest itself does not write runtime state, but it controls compilation artifacts under Cargo target directories and the linked runtime behavior of TiKV binaries, including selected allocator, storage engine test features, OpenSSL linkage, and profiling support.

## Dependencies and integration points
It integrates every major TiKV component crate, command crates, fuzz/test crates, git dependencies (`raft-engine`, `kvproto`, `tipb`, `yatp`, patched protobuf/raft), and tooling such as cargo-machete. It is consumed by Cargo, Makefile targets, CI, Docker builds, and release scripts.

## Risks and edge cases
Large feature surfaces can produce accidental feature combinations, especially around allocator and RocksDB options. Git patches and forks increase supply-chain and reproducibility sensitivity. `openssl-vendored` is used to support static/FIPS-related builds but can lengthen builds. Profile choices disable some debug/overflow checks in dev for speed, which may hide issues outside tests.

## Test signals
Signals include `cargo metadata`, `cargo build --workspace --no-default-features --features ...`, `make clippy`, `make test`, cargo-machete ignored-dependency behavior, and release/profile builds for both `tikv-server` and `tikv-ctl`.
