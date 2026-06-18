# sources/storage-engines/tikv/components/in_memory_engine/Cargo.toml

Purpose: manifest for the `in_memory_engine` crate implementing TiKV’s region cache memory engine.

Important APIs/types/functions: features `testexport` and `failpoints`; failpoints test target; Criterion `load_region` bench; dependencies for concurrency, engine traits, RocksDB, raftstore, PD, metrics, config, async runtimes, and MVCC types.

Control flow: no runtime flow; controls feature-gated tests and benchmark compilation.

State and persistence: none in manifest, but dependencies show the crate bridges in-memory cache state with disk snapshots and raftstore.

Dependencies/integration: consumed by `hybrid_engine` and raftstore/storage integration.

Risks: broad workspace coupling; normal `fail` dependency plus feature-gated failpoints requires build discipline.

Test signals: manifest exposes failpoint tests, proptest support, and load-region benchmark.
