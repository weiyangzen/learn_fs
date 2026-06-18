# sources/storage-engines/tikv/components/hybrid_engine/src/util.rs

Purpose: test utility for constructing a temporary RocksDB-backed `HybridEngine` with a configured `RegionCacheMemoryEngine`.

Important APIs/types/functions: `hybrid_engine_for_tests(prefix, config, configure_memory_engine_fn)` returning `(TempDir, HybridEngine<RocksEngine, RegionCacheMemoryEngine>)`.

Control flow: creates temp dir, opens RocksDB with data CFs, creates memory engine test context, attaches disk engine, runs caller configuration closure, and returns the hybrid engine.

State and persistence: temporary RocksDB state lives under `TempDir`; memory cache state is configured by the closure.

Dependencies/integration: used across hybrid engine tests; depends on Rocks engine, in-memory engine config/context, `tempfile`, and `VersionTrack`.

Risks: public utility is test-oriented and should not be used for production storage setup.

Test signals: doctest-style example and broad use in module tests.
