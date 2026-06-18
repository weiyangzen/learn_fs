# sources/storage-engines/tikv/cmd/tikv-server/Cargo.toml

## Purpose
This manifest defines the `tikv-server` binary crate. It is intentionally small and depends on the workspace `tikv`, `server`, `crypto`, and utility crates to build the production TiKV executable.

## Important APIs, Types, And Functions
As a Cargo manifest, it exposes features rather than Rust APIs. Key features include allocator choices (`tcmalloc`, `jemalloc`, `mimalloc`), portability/SSE, memory profiling, failpoints, OpenSSL vendoring, async task tracing, tablet lifetime tracing, pprof failpoint support, and test-engine selections. Default features enable RocksDB KV test engine and raft-engine test support.

## Control Flow
Cargo uses this file to select optional dependencies and feature forwarding. Most feature flags are simple pass-throughs to `server` or `tikv`; `trace-async-tasks` additionally enables `tracing-active-tree` and `tracing-subscriber`.

## State And Persistence Behavior
No runtime state is directly managed here. Feature selection affects allocator behavior, instrumentation, failpoint compilation, and engine availability in the compiled binary.

## Dependencies And Integration Points
The crate depends on `clap`, `crypto`, `server`, `tikv`, `tikv_util`, `toml`, `serde_json`, and optional tracing crates. Build dependencies are `cc` and workspace `time`, inherited through the included build script.

## Risks And Edge Cases
- Feature combinations can significantly change binary behavior and available tests.
- Default test-engine features in a production-looking binary crate require workspace conventions to avoid accidental mismatch.
- Optional allocator features must remain mutually sensible with downstream `server` feature constraints.

## Test Signals
Cargo feature resolution and workspace CI are the primary signals. There are no manifest-local tests, but compile jobs with allocator, failpoints, tracing, and test-engine permutations are relevant.
