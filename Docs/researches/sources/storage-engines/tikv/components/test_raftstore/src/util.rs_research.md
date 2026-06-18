# Research: sources/storage-engines/tikv/components/test_raftstore/src/util.rs

## sources/storage-engines/tikv/components/test_raftstore/src/util.rs

Purpose: large raftstore test utility module for request construction, engine bootstrap, storage assertions, transactional gRPC helpers, region/log checks, and cluster tuning. It exports `HybridEngineImpl` and reexports peer constructors. APIs cover `must_get*`, request builders for raft commands/admin/status, callback creation, async read/snapshot helpers, engine creation, config mutators, raw/MVCC KV helpers, lock/status assertions, `PeerClient`, region peer lookup, sync waits, and delete-range checks.

Control flow is mostly helper orchestration. Reads and writes build protobuf requests with contexts/epochs, create callbacks through `make_cb`, submit to `Cluster` or `Simulator`, then assert responses. `create_test_engine` and `start_test_engine` allocate temp dirs, configure data/raft paths, encryption, Rocks env/cache, raft engine, SST recovery worker, coprocessor region accessor, and KV engine factory. KV helpers compose prewrite/commit/rollback/check/status gRPC calls.

State and persistence are test-local: temporary Rocks/raft DBs, encryption key files, background SST recovery workers, generated random keys, raft apply/truncated states, and cluster PD timestamps. Dependencies span engine traits, Rocks, raftstore, TiKV storage/server configs, kvproto, failpoints, futures, tempfile, PD client, and txn types.

Risks include retry loops masking slowness, many `unwrap`/panic assertions, assumptions about region 1, raw key encoding, GC/log compaction timing, and maintaining correctness across API versions. Test signals are the module itself: every helper encodes an expected outcome and several helpers (`check_compacted`, `must_region_cleared`, `wait_for_synced`) validate persistence side effects.
