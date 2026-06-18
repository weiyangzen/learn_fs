# sources/storage-engines/tikv/components/test_raftstore/src/common-test.toml

Purpose: this TOML file defines the common TiKV test configuration used by the legacy raftstore harness. It shrinks thread pools, ports, timeouts, caches, and background work so multi-store integration tests run quickly and deterministically on local temp directories.

Important settings: read pools are unified and set to one thread; server address is `127.0.0.1:0`; gRPC concurrency and raft connection counts are low; storage scheduler concurrency is modest; block cache is 64 MB; raftstore tick intervals and heartbeat/election values are short; log GC, raft-engine purge, PD heartbeat, split/merge checks, and region flow reporting run quickly; hibernate regions and dev assertions are enabled; store IO pool is disabled in the legacy config; apply/store/snapshot generator pools are small; RocksDB/RaftDB background jobs and Titan GC are constrained; resolved-ts is disabled by default.

Control flow: this file is consumed by config construction helpers rather than executed. `Config::new` copies the loaded `TikvConfig` and points `cfg_path` at a temp config file so online-config tests do not mutate this shared TOML.

State and persistence behavior: default paths are supplied elsewhere by temp dirs. The config affects persistent behavior indirectly by accelerating raft log GC, snapshot generation/GC, stale-peer checks, compaction, and import/GC workers. Short durations make state transitions observable inside typical test timeouts.

Dependencies and integration points: sections map to TiKV config modules: `readpool`, `server`, `storage`, `raftstore`, `rocksdb`, `raftdb`, `security`, `import`, `gc`, `pessimistic-txn`, and `resolved-ts`. The same defaults influence both node and server clusters unless tests mutate them.

Risks and test signals: these settings are intentionally non-production. Very short raft and PD intervals can reveal races in tests but may also make timing-sensitive tests flaky under heavy load. Changing a duration here affects many integration tests globally. The v2 cluster overrides store IO pool to at least one because raftstore v2 always uses async write.
