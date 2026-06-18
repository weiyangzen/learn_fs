<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/Cargo.toml -->
# sources/security-integrity/cryfs/crates/blockstore/Cargo.toml

## Purpose
Package manifest for `cryfs-blockstore`, declaring the crate metadata, dependencies, optional test utilities, and platform-specific dependencies.

## APIs, Flow, And State
The package inherits workspace authors, edition, Rust version, homepage, repository, license, readme, and version. Core dependencies include async/runtime libraries, binary encoding, byte sizing, crypto/utils/version crates, futures, locking, compression, random/hex, serialization, system info, and Tokio filesystem/stream support. Optional `mockall` and `tempfile` are enabled by the `testutils` feature.

## Dependencies And Integration
Uses Unix `libc` except wasm/unknown targets and Windows `winapi` with `fileapi`. Dev dependencies add common macros, `cryfs-utils` testutils, `generic-array`, `mockall`, `tempfile`, and `pretty_assertions`.

## Risks And Test Signals
Feature gating is important: production builds should not pull mock/tempfile unless `testutils` is enabled. The crate root also asserts `byte_unit::Byte` size and cargo/git version consistency, which are integration-level signals tied to this manifest.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/Cargo.toml -->
