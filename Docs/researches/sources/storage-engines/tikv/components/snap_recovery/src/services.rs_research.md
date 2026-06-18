# sources/storage-engines/tikv/components/snap_recovery/src/services.rs

Purpose: implements the snapshot recovery gRPC service (`RecoverData`) that BR drives to collect region metadata, assign leaders, wait raft apply, and resolve KV data.

Important APIs and types: `RecoveryService<EK, ER>` stores engines, raft router, a 4-thread futures pool, and `last_recovery_region_rpc` for aborting overlapping recover-region tasks. `RecoverRegionState` wraps abortable futures and records start/finished state. `set_db_options` raises RocksDB level0 slowdown/stop triggers. `wait_apply_last` broadcasts a relaxed snapshot wait-apply request. `compact` manually compacts every CF after data resolution.

Control flow: `new` creates the worker pool and configures every Rocks CF for recovery. `read_region_meta` starts `RegionMetaCollector`, streams collected `RegionMeta` values to the server-streaming sink, and aborts any previous recover-region task. `recover_region` consumes a client stream, separates requested leaders/followers, runs `LeaderKeeper::elect_and_wait_all_ready`, sends per-leader `SnapshotBrWaitApply` requests and awaits oneshots, then returns store id. It replaces/aborts any prior recovery-region task. `wait_apply` broadcasts wait-apply to all regions and responds after the shared syncer fires. `resolve_kv_data` starts `DataResolverManager`, streams progress with store id, runs manual compaction, and closes the stream.

State and persistence behavior: mutates RocksDB options, raft leadership, raft apply synchronization, and KV data through `DataResolverManager`. `compact` performs manual compactions on all CFs with high subcompaction count and skips bottommost-level compaction. Overlapping recovery-region RPC state is in-memory and abortable.

Dependencies and integration points: integrates grpcio, recoverdata protobuf service trait, raftstore router/significant messages, snapshot backup wait-apply syncer, `LeaderKeeper`, `RegionMetaCollector`, `DataResolverManager`, Rocks compaction APIs, and recovery metrics.

Risks: recovery RPCs are stateful and ordering-sensitive. `recover_region` starts work only after the client closes its send stream; a stuck leader election can keep the call open until another RPC aborts it. `read_region_meta` aborts prior recover-region tasks as a protocol workaround. Many errors are logged rather than sent as structured RPC failures. Manual compaction and data deletion are heavy operations on production data. `set_db_options` unwraps Rocks option setting.

Test signals: `test_state` validates abortable recovery task state: aborting a pending future yields `Aborted`, and a completed future flips the finished flag.
