# sources/storage-engines/tikv/src/server/raftkv2/raft_extension.rs

Purpose: bridges raftstore-v2 `StoreRouter` to `tikv_kv::RaftExtension` for network transport, split, snapshot-status, reachability, tombstone, and region-query operations.

Important APIs/types/functions: `Extension<EK, ER>`; `new`; `feed`; `report_peer_unreachable`; `report_store_unreachable`; `report_store_maybe_tombstone`; `report_snapshot_status`; `split`; `query_region`.

Control flow: `feed` boxes and forwards raft messages, logging only key-message failures. Reachability and tombstone methods send peer/store messages. Snapshot status is force-sent to the target region. `split` sends `PeerMsg::request_split`, waits for subscription result, and returns regions or header error. `query_region` sends `QueryDebugInfo` over a debug channel.

State/persistence: no local durable state; operations affect raftstore-v2 state through peer/store FSMs.

Dependencies/integration: used by `RaftKv2::raft_extension`, server transport, snapshot handling, and debug. Depends on v2 router message types and legacy `RegionMeta` for query compatibility. Risks: `report_reject_message` and `report_resolved` are TODO/no-ops; snapshot-status send errors are ignored; split/query can abort if subscriptions close. No local tests.
