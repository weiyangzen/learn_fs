# sources/storage-engines/raft-engine/Cargo.toml

## Purpose
Declares the raft-engine crate metadata, examples, tests, benchmarks, dependencies, features, patches, and workspace members.

## Important APIs, Types, And Functions
The package is `raft-engine` version 0.4.2, edition 2024, Rust 1.85.0. It declares examples `append-compact-purge` and `raft-engine-fork`, a failpoints integration test requiring internals/failpoints, and a benchmark requiring failpoints. Features include default `internals` and `scripting`, plus `nightly`, `failpoints`, `swap`, `std_fs`, and `nightly_group`.

## Control Flow
Cargo uses this manifest to build the library, examples, workspace members `stress` and `ctl`, and optional feature combinations selected by the Makefile and CI. `docs.rs` is configured to build with `internals`.

## State And Persistence Behavior
The manifest controls binary and library dependency resolution rather than runtime state. Feature choices materially affect persistence behavior: `swap` enables memory-limit behavior via memmap, `std_fs` selects a plain file descriptor path, failpoints enable injected I/O failures, and `scripting` enables repair tooling.

## Dependencies And Integration Points
Dependencies include byte encoding, CRC, failpoints, fs locking, logging, compression, protobuf, prometheus, serde, Rhai scripting, and error handling. Dev dependencies bring raft/kvproto protobuf types, random testing, temp files, TOML, and benchmarks. Patches pin raft-proto/protobuf forks and cc-rs.

## Risks And Edge Cases
Git dependencies and patch overrides can make reproducibility depend on upstream branches. Root crate Rust version is newer than `ctl`'s local manifest. Pinned `lz4-sys` and `cc` reflect build compatibility constraints. Default inclusion of `scripting` and `internals` broadens normal builds.

## Test Signals
Cargo metadata is exercised by `make clippy`, `make test`, CI matrix, examples, failpoint tests, and docs.rs feature builds.
