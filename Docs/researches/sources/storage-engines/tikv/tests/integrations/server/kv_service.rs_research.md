# sources/storage-engines/tikv/tests/integrations/server/kv_service.rs

Purpose: broad TiKV KV service integration coverage across raftstore v1 and v2. It validates raw KV, transactional KV, debug APIs, batch streaming, forwarding, health, lock management, quotas, execution details, pipelined DML, API versions, cluster IDs, and `need_commit_ts`.

Important APIs and functions: raw compare-and-swap/get/put/scan/delete/TTL APIs; transaction prewrite/commit/get/scan/batch-get/scan-lock/rollback/cleanup/resolve-lock/delete-range/MVCC debug/flashback/pessimistic-lock/check-status/heartbeat APIs; debug store/get/raft-log/region-info/region-size/failpoint/scan-MVCC APIs; `batch_commands`; health feedback; forwarding macros `test_func!`/`test_func_init!`; `test_with_memory_lock_cluster`; `ConcurrencyManager`, `QuotaConfig`, `CollectorRegHandle`, raft engines, and CF constants.

Control flow: tests start clusters and clients through `test_raftstore` or `test_raftstore_v2` constructors, execute RPCs, and assert response fields, region/key errors, execution details, stream counts, or direct engine state. Early tests cover raw KV/TTL and MVCC read/write/rollback/GC/flashback. Debug tests seed engine or raft-engine state and verify debug RPCs. Batch and forwarding tests exercise duplex streams, health feedback, proxy routing, and reconnect behavior. Later tests cover pessimistic locks, async commit, max commit timestamp fallback, in-memory lock reads, lock wait info, API-version validation, quota timing, write-detail metrics, scan-lock over memory and CF locks, read-first pessimistic rollback, pipelined DML flush/buffer/conflicts, cluster-id validation, and commit-ts return fields.

State and persistence: exercises persisted RocksDB and raft-engine state plus in-memory lock state. It writes raw TTL records, MVCC default/write/lock CF entries, raft log/state records, pipelined DML buffered locks, and debug data. It verifies flashback blocks newer reads/writes and scheduling, GC removes old versions, quota settings delay writes, and invalid cluster IDs do not advance max timestamp.

Dependencies and integration: `kvproto::tikvpb::TikvClient`, raftstore v1/v2 harnesses, gRPC unary and streaming APIs, debugpb clients, health checking, storage scheduler, concurrency manager, API-version encoding, raft engines, resource metering collector handle, quota config, failpoints, and TiKV server forwarding.

Risks: high timing/concurrency surface from sleeps, timeouts, lock waits, gRPC streams, quota assertions, and failpoint-driven flashback failures. Exact protocol details such as error kinds, sequence numbers, API-version abort strings, and cluster-id INVALID_ARGUMENT behavior are tightly asserted.

Test signals: end-to-end confidence that TiKV public KV service behavior is consistent across raftstore v1/v2 for raw, transactional, debug, proxy, streaming, lock, flashback, pipelined DML, validation, and execution-accounting paths.
