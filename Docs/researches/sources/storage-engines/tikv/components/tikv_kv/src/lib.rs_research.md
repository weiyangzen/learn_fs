# sources/storage-engines/tikv/components/tikv_kv/src/lib.rs

Purpose: this is the public core of `tikv_kv`, defining the storage-engine abstraction used by raft-backed KV, test RocksDB engines, BTree engines, cursor tests, and region snapshots. It re-exports engine implementations, cursor helpers, raft extensions, Rocks snapshots, and statistics types, so most downstream storage code imports this module rather than individual implementation files.

Important APIs: `Modify` models writes (`Delete`, `Put`, `PessimisticLock`, `DeleteRange`, `Ingest`) and converts to/from `raft_cmdpb::Request`; `WriteData` carries modifies plus `TxnExtra`, deadline, disk-full policy, and batching hints; `WriteEvent` models proposed/committed/finished stream events. `Engine` is the central trait with associated snapshot/local engine types, async snapshot/write operations, local modification, flashback hooks, region seek, and helper methods (`write`, `put_cf`, `delete_cf`, `snapshot`). `Snapshot`, `SnapshotExt`, and `Iterator` define the low-level consistent view and seek/scan API.

Control flow: sync helpers wrap async trait methods with `block_on_timeout(DEFAULT_TIMEOUT)`. `write()` consumes the engine write stream until `WriteEvent::Finished`. `snapshot()` and `in_memory_snapshot()` record tracker latency around the async snapshot future and expose a failpoint after acquisition. `write_modifies()` translates each `Modify` into a local `WriteBatch`, special-casing default CF, lock CF serialization, delete-range `notify_only`, and unsupported SST ingestion.

State and persistence: persistence is delegated to `Engine::Local` and `WriteBatch`; this file stores only request structs and a thread-local raw pointer (`TLS_ENGINE_ANY`) for per-thread engine access. `LocalTablets` abstracts singleton versus registry-backed tablet lookup.

Dependencies and integration: integrates `engine_traits`, `kvproto`, `raftstore`, `txn_types`, `tracker`, failpoints, and TiKV utility timing/memory helpers. Raft request conversion is a critical integration point with raftstore command proposal.

Risks: unsafe TLS pointer APIs require exact engine type on destroy; `Modify::size()` and `key()` intentionally panic for range/ingest variants; default timeouts can mask hung engines; request-to-modify conversion is test-oriented and only supports selected raft command types. Empty writes are expected to error.

Test signals: embedded tests cover modify/request round trips, CRUD, CF access, seek/near-seek behavior, statistics increments, empty writes, and cursor behavior under multiple scan modes.
