<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs

## Purpose
Defines the public module boundary for RustFS erasure coding. It wires together bitrot framing, stream decode, stream encode, core Reed-Solomon operations, and healing.

## Important APIs, types, and functions
The module declares private `bitrot`, public `decode`, `encode`, `erasure`, and `heal` submodules. It re-exports all public items from `bitrot`, plus `Erasure`, `ReedSolomonEncoder`, `calc_shard_size`, and `calc_shard_size_legacy` from `erasure`.

## Control flow
There is no runtime control flow in this file. Compile-time module declarations make `decode`, `encode`, `erasure`, and `heal` addressable as submodules, while re-exports shorten common imports for callers that need bitrot wrappers or the core erasure type.

## State and persistence behavior
The file holds no state and performs no persistence. Its persistence relevance is API-level: re-exported shard sizing functions and `Erasure` are the entry points that downstream object metadata and storage code use to encode, decode, and interpret persisted shard files.

## Dependencies and integration points
Integrates the sibling files in `erasure_coding`. External callers can import `crate::erasure_coding::BitrotReader`, `BitrotWriterWrapper`, `Erasure`, and sizing helpers without referencing the private `bitrot` module path. The public submodules allow tests or callers to reach `decode`, `encode`, `erasure`, and `heal` APIs directly where visibility permits.

## Risks and test signals
Because `bitrot` is private but re-exported wholesale, any new public item in `bitrot.rs` automatically becomes part of this module's public API. Conversely, only selected symbols from `erasure.rs` are re-exported, so new core helpers require explicit export decisions. Test signal is indirect through all submodule tests; there are no module-only tests needed unless API visibility changes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs -->
