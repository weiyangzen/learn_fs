# sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs

Purpose: a no-auth gRPC lock client used by distributed lock e2e tests. It adapts RustFS `node_service` lock RPCs to the `rustfs_lock::LockClient` trait so `NamespaceLock` can be exercised over real tonic channels without production auth plumbing.

Important APIs and types: `GrpcLockClient { addr }` stores a remote endpoint. `new` constructs it. `get_client` uses `rustfs_ecstore::rpc::node_service_time_out_client_no_auth`. `create_unlock_request` reconstructs a minimal `LockRequest` from a `LockId` for unlock-like RPCs. `build_lock_info` deserializes server-provided `LockInfo` JSON or synthesizes fallback lock info from the request.

Control flow: `acquire_lock` serializes a `LockRequest` to JSON in `GenerallyLockRequest.args`, calls `lock`, and maps success or server error text to `LockResponse`. `acquire_locks_batch` serializes many requests, calls `lock_batch`, and aligns returned results by index, producing explicit failures for missing entries. `release`, `refresh`, and `force_release` serialize the minimal request and call `un_lock`, `refresh`, or `force_un_lock`, turning `error_info` into `LockError`. `release_locks_batch` calls `un_lock_batch` and returns booleans aligned to input lock IDs. `check_status` has no direct remote status endpoint; it probes by attempting an exclusive lock and immediately releasing it if successful, otherwise returns generic acquired lock info. `get_stats` returns default stats with `last_updated`; `is_online` sends `PingRequest`; `is_local` is always false.

State and persistence: the client owns no lock state beyond the endpoint string. Remote lock state lives in the server-side `LockClient` implementation reached through gRPC. Fallback `LockInfo` timestamps are local approximations, not persisted facts.

Dependencies and integration points: `rustfs_lock` trait and types, `rustfs_protos::node_service`, tonic `Request`, serde JSON serialization, no-auth RPC connection helper, and `tracing`.

Risks: status probing can briefly acquire and release a lock, which can perturb state and is only approximate. Unlock/refresh/force-release requests use default owner/type/TTL fields because the RPC interface requires a full `LockRequest`; server behavior must rely on `lock_id`. Batch response length mismatches degrade to failures but may hide server-side ordering bugs. Fallback lock info can mask serialization incompatibility.

Test signals: consumed by `lock.rs` tests for quorum behavior, batch acquire/release, lock-id preservation, missing release errors, and health checks over live gRPC channels.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/grpc_lock_client.rs -->
