# sources/storage-engines/tikv/components/tidb_query_datatype/Cargo.toml

## Purpose
Defines the `tidb_query_datatype` Rust crate, which houses TiDB pushed-down query data types, codecs, collations, MySQL value representations, and related builders.

## APIs, Flow, And State
This manifest sets package metadata, Rust 2021 edition, unpublished status, Apache-2.0 licensing, and a Criterion benchmark target `bench_vector_distance`. It pulls in workspace crates such as `codec`, `kvproto`, `tidb_query_common`, `tipb`, `tikv_alloc`, and `tikv_util`, plus serialization, numeric, collation/encoding, regex, logging, and error crates. `criterion` is dev-only.

## Dependencies And Integration
The crate is part of TiKV's workspace and integrates with protobuf schemas (`tipb`, `kvproto`), storage/query common code, and codec primitives. The pinned TiKV fork of `encoding_rs` is an important charset dependency for collation/encoding behavior.

## Risks And Test Signals
The manifest's risks are dependency drift, pinned git dependency availability, and feature compatibility with workspace crates. Test signal is indirect: crate compilation, unit tests in codec/collation modules, and the Criterion benchmark target.
