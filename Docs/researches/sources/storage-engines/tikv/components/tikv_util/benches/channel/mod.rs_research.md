# sources/storage-engines/tikv/components/tikv_util/benches/channel/mod.rs

Purpose: minimal benchmark crate root for the `tikv_util` channel benchmarks.

Important APIs: enables `#![feature(test)]`, imports the unstable `test` crate, and includes the `bench_channel` module.

Control flow: Cargo invokes this file as the bench target configured in `Cargo.toml`; Rust's benchmark harness discovers the `#[bench]` functions in `bench_channel.rs`.

State and persistence: no runtime state beyond benchmark harness initialization.

Dependencies and integration: relies on nightly Rust bench support and the `test` crate. It connects the manifest's `[[bench]]` entry to the actual benchmark module.

Risks: requires nightly/unstable feature support; this root will fail under stable-only bench execution. Any additional bench modules must be manually declared here.

Test signals: successful compilation confirms the bench harness and module wiring.
