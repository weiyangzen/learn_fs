# sources/storage-engines/tikv/components/causal_ts/Cargo.toml

## Purpose
Defines the `causal_ts` crate, which provides causal timestamp provider abstractions and PD-backed TSO caching.

## APIs, Types, And Functions
The package is non-published, edition 2021, with a `testexport` feature. Dependencies include async traits, enum dispatch, PD client, prometheus, parking_lot, tokio sync, TiKV worker/utilities, and transaction timestamps. A Criterion bench target `tso` is defined.

## Control Flow
Cargo feature selection controls test exports and benchmark availability. The manifest keeps `test_pd_client` in dependencies because both `lib.rs` and benches require it.

## State And Persistence
No runtime state in the manifest. It configures compilation and dependency graph.

## Dependencies And Integration Points
Shows core integration with PD, transaction timestamp types, metrics, and test PD clients. This crate is consumed by CDC and other components needing causal timestamps.

## Risks And Test Signals
Keeping test client dependencies in normal dependencies is noted as a TODO and may affect dependency surface. The explicit `tso` benchmark signals performance sensitivity of timestamp cache operations.
