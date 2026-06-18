# sources/storage-engines/tikv/src/server/service/debug.rs

Purpose: implements the gRPC Debug service by delegating engine/raft/config/metrics/flashback/read-progress operations to a debug runtime, `Debugger`, raft extension, and store metadata.

Important APIs/types/functions: `Service<T, D, S>`; `ScheduleResolvedTsTask`; `handle_response`; error mapping helpers; Debug trait RPC methods.

Control flow: unary RPCs spawn work on the debug pool, transform debugger results into protobuf responses, and use `handle_response` for success/failure. `scan_mvcc` streams iterator rows. `check_region_consistency` calls raft extension `check_consistency`. `reset_to_version` starts reset and immediately replies. `flashback_to_version` awaits debugger flashback. `get_region_read_progress` reads region read-progress state under store-meta lock, then calls resolved-ts scheduler via paired future and merges resolver info.

State/persistence: service holds runtime/debugger/router/meta references. RPCs can mutate live state: failpoints, config, compaction, reset-to-version, flashback, and consistency hash admin command.

Dependencies/integration: `Debugger`, `tikv_kv::RaftExtension`, `StoreRegionMeta`, grpcio, failpoints, metrics dump, paired futures, and debug protobufs. Risks include powerful mutating debug surface, unwraps on spawned task joins, reset not waiting for completion, and silent return on scan iterator creation failure. Coverage is mostly debugger/integration tests.
