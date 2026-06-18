# sources/storage-engines/tikv/components/hybrid_engine/src/observer/load_eviction.rs

Purpose: raftstore coprocessor observer translating region lifecycle, apply, and transfer-leader events into region-cache load/eviction events.

Important APIs/types/functions: `LoadEvictionObserver`, `register_to`, `post_exec_cmd`, `split_region`, `merge_region`, `try_load_region`, `evict_region`, and observer trait impls for query/admin/snapshot/role/destroy-peer/transfer-leader.

Control flow: delete range evicts by range; ingest SST and prepare merge evict; commit/rollback merge evict then reload; split sends split event; prepare flashback and apply snapshot evict; leader transition tries manual load; follower transition evicts; destroy peer evicts; transfer leader custom context requests/preloads cache on transferee before ack.

State and persistence: observer has no durable state; cache engine receives `RegionEvent`s and owns actual state. Metrics record warmup behavior.

Dependencies/integration: deeply integrated with raftstore coprocessor, `RegionCacheEngineExt`, kvproto, raft, keys, and TiKV logging.

Risks: event ordering affects cache correctness; invalid transfer context falls back to ready and skips warmup; merge reload is asynchronous.

Test signals: mock-engine tests cover split non-eviction, ingest-SST eviction, and leader try-load.
