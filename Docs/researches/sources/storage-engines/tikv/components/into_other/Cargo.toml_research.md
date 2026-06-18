# sources/storage-engines/tikv/components/into_other/Cargo.toml

## Purpose
This manifest defines the private `into_other` crate, a small conversion crate used to avoid direct dependency cycles between error-producing crates and consumers that need protocol or Raft errors.

## Important APIs, Types, and Functions
The manifest exposes no code itself. It names the crate, sets Rust 2021 edition, marks it unpublished, and declares dependencies on `engine_traits`, `kvproto`, and `raft`.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
The dependency set matches `src/lib.rs`: `engine_traits::Error` is converted into `kvproto::errorpb::Error` and `raft::Error`.

## Risks
The crate's reason to exist is dependency separation. Adding broad dependencies here could reintroduce coupling or cycles in TiKV's component graph.

## Test Signals
There are no local tests in the manifest. Compile success of downstream crates is the primary signal.
