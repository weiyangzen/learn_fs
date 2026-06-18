# sources/storage-engines/tikv/components/hybrid_engine/Cargo.toml

Purpose: manifest for the `hybrid_engine` crate, a private TiKV workspace crate composing RocksDB with the in-memory region cache.

Important APIs/types/functions: declares package metadata, runtime dependencies on engine traits/implementations, raftstore, kvproto, metrics, config, and utilities, plus failpoint/test dependencies.

Control flow: no runtime code; controls compile-time integration and test availability.

State and persistence: none directly; dependencies provide RocksDB persistence and memory-cache state.

Dependencies/integration: bridges `engine_rocks`, `in_memory_engine`, `engine_traits`, and raftstore observers.

Risks: duplicate `tempfile` normal/dev dependency appears intentional for public test utility but should be kept in mind; edition 2024 requires matching workspace toolchain.

Test signals: dev dependencies support failpoint and temp-engine tests found in the crate.
