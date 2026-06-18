# sources/object-store/garage/src/model/Cargo.toml

Purpose: This manifest defines the `garage_model` crate, the core data model layer for Garage's object store.

Important APIs and types: Package metadata sets name `garage_model`, version `2.3.0`, AGPL license, repository, and readme. The library path is `lib.rs`. Features include default `lmdb` and `sqlite`, optional `k2v`, `fjall`, and `arbitrary`.

Control flow: Cargo resolves this crate's dependencies and feature flags from the manifest. Feature selection controls database backend support and optional K2V/arbitrary code paths in the model crate.

State and persistence behavior: The manifest does not execute persistence itself, but it selects dependencies responsible for metadata tables, RPC integration, block references, database engines, compression, hashing, and serialization used by Garage's persisted model state.

Dependencies and integration points: It depends on internal crates `garage_db`, `garage_rpc`, `garage_table`, `garage_block`, `garage_util`, and `garage_net`, plus argon2, async-trait, blake2, chrono, thiserror, hex, http, base64, parse_duration, tracing, rand, zstd, serde, serde_bytes, futures, and tokio.

Risks: Default-enabling both LMDB and SQLite increases build surface. Backend feature combinations must remain aligned with top-level binary compile checks. The `k2v` feature only enables `garage_util/k2v` here, so related crates must coordinate feature flags.

Test signals: All Garage integration tests exercise `garage_model` indirectly through bucket/key/object/K2V/website state. This manifest itself is validated by workspace builds and feature-enabled test compilation.
