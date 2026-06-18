# sources/object-store/rustfs/crates/ecstore/src/rpc/remote_locker.rs

## Purpose

`remote_locker.rs` implements `rustfs_lock::LockClient` for locks hosted by another RustFS node. `RemoteClient` is a thin, signed gRPC adapter around the node-service lock RPCs. It serializes local lock requests to JSON, sends unary protobuf requests to the remote node, converts remote success/error responses back into `LockResponse` and lock-state types, and evicts cached channels when lock RPCs time out or return tonic failures.

The implementation is intentionally not a local lock store. It has no persistent lock table of its own and relies on the remote node service for actual acquisition, release, refresh, force-release, and batch behavior.

## Important APIs, Types, and Functions

- `RemoteClient`: cloneable wrapper containing the remote node base address string.
- `RemoteClient::new` and `RemoteClient::from_url`: constructors from an endpoint string or parsed URL.
- `get_client`: creates or retrieves a signed `NodeServiceClient<InterceptedService<Channel, TonicInterceptor>>` through `node_service_time_out_client` and `gen_tonic_signature_interceptor`.
- `build_ping_request`: creates a flatbuffer-backed `PingRequest` payload used by `is_online`.
- `create_unlock_request`: builds a minimal `LockRequest` from a `LockId` for unlock, refresh, force-unlock, and status-probe paths where the server mainly needs the lock ID/resource.
- `execute_rpc`: wraps acquisition RPCs in a timeout, logs tonic failures/timeouts, evicts cached connections, and maps failures into `LockError`.
- `rpc_timeout`: clamps zero-duration lock timeouts to 1 ms so remote acquisition RPCs cannot accidentally wait forever.
- `rpc_failure_response`, `rpc_timeout_failure_response`, and batch variants: convert transport-layer failures into normal failed `LockResponse` values for acquisition APIs.
- `batch_rpc_timeout`: chooses the maximum acquire timeout from a batch and applies the same zero-timeout clamp.
- `build_lock_info`: uses server-provided `lock_info` JSON when available, otherwise synthesizes a `LockInfo` from the original request.
- `LockClient for RemoteClient`: implements acquire, batch acquire, release, batch release, refresh, force release, status check, stats, close, online check, and local/remote check.

## Control Flow

Single lock acquisition logs the resource, gets a signed client, serializes the `LockRequest` into `GenerallyLockRequest.args`, and calls `client.lock` through `execute_rpc` with `request.acquire_timeout`. Timeout and tonic transport failures are returned as successful Rust `Ok(LockResponse { success: false, ... })` values so the distributed lock layer can treat unreachable remote acquisition as lock acquisition failure rather than a client exception. A successful server response becomes `LockResponse::success` with either decoded or synthesized `LockInfo`; an application-level server rejection becomes `LockResponse::failure`.

Batch acquisition is similar. It returns early for an empty request list, serializes all requests into `BatchGenerallyLockRequest.args`, chooses the maximum request acquire timeout for the RPC, and maps each returned result by index. Missing response entries become per-request failed responses, preserving output length and request ordering.

Release, batch release, refresh, and force release use the minimal unlock request shape and call the corresponding node-service methods directly (`un_lock`, `un_lock_batch`, `refresh`, `force_un_lock`). Unlike acquisition, these paths do not use `execute_rpc`; tonic errors become `Err(LockError::internal(...))`, and server `error_info` is also returned as an error.

`check_status` is an approximation because the node-service API has no direct status query. It tries to acquire an exclusive lock using a minimal request. If that succeeds, it releases it best-effort and returns `None`, meaning the lock was likely free. If acquisition fails, or if communication fails, it returns a generic `LockInfo` with owner `unknown`, exclusive type, acquired status, default metadata, normal priority, and a synthetic expiration time.

`get_stats` returns default stats with `last_updated` set to now because there is no remote stats RPC. `is_online` gets a client and sends a flatbuffer ping request; client creation or ping failure returns false, while any ping success returns true.

## State and Persistence Behavior

`RemoteClient` stores only `addr`. It does not persist locks, cache lock ownership, or maintain local counters. All durable or time-bound lock state lives on the remote lock service. Local behavior that does affect process state includes:

- cached tonic channels managed by the shared connection map behind `node_service_time_out_client`;
- eviction of cached connections through `evict_failed_connection` on acquisition timeout or tonic failure;
- synthesized `LockInfo` timestamps using `SystemTime::now()` when the server does not return lock info or when status is approximated.

The timeout clamp is a state-safety guard: a zero acquire timeout becomes a 1 ms remote RPC timeout instead of an unbounded wait.

## Dependencies and Integration Points

Key dependencies include:

- `rustfs_lock`: `LockClient`, `LockRequest`, `LockResponse`, `LockId`, `LockInfo`, `LockStats`, `LockError`, lock status/type/metadata/priority models, and the result alias.
- `rustfs_protos`: node-service protobufs for single and batch lock requests, ping requests, ping flatbuffer body builder, node-service client, and cached connection eviction.
- `crate::rpc::client`: signed tonic interceptor and shared node-service client factory.
- `tonic`, `tokio::time::timeout`, `bytes`, `flatbuffers`, `serde_json`, `url`, and `tracing`.

This client is used by higher-level distributed locking code through the `LockClient` trait. It must stay wire-compatible with the node-service lock server, including the JSON shape placed in `GenerallyLockRequest.args` and `BatchGenerallyLockRequest.args`. It also participates in shared RPC connection lifecycle through `GLOBAL_CONN_MAP` indirectly, because evicting a failed lock connection removes the cached channel for the node address.

## Risks and Edge Cases

- Acquisition methods turn transport failures into failed lock responses, while release/refresh/force-release methods return `Err`. Callers must understand this asymmetry.
- `release`, `release_locks_batch`, `refresh`, `force_release`, `check_status`, and `is_online` do not use `execute_rpc`, so they do not get the same explicit timeout wrapper or cache eviction behavior on timeout/failure.
- `create_unlock_request` fills owner, type, timeout, TTL, and metadata with defaults because the server is expected to key off `lock_id`. If server behavior starts validating more fields, these minimal requests can break.
- `check_status` is not authoritative and can perturb state briefly by acquiring and releasing a free lock. On communication errors it reports a generic held lock, which is conservative but may hide node reachability failures.
- `build_lock_info` silently falls back to synthesized info if server lock-info JSON is malformed. That keeps acquisition usable but can mask schema drift.
- The special scanner leader lock `.rustfs.sys/leader.lock@latest` downgrades some timeout/failure logs to debug. This reduces noise for expected contention or scanner behavior, but can also hide repeated leader-lock reachability problems unless debug logs are enabled.
- Batch acquisition uses the maximum acquire timeout across requests. One long-timeout request can make the entire batch RPC wait longer than smaller requests would individually.
- The ping health check validates node-service reachability, not remote lock correctness or availability.

## Test Signals

The in-file tests focus on timeout and connection-cache behavior:

- A hanging TCP listener plus a cached lazy tonic channel verifies `acquire_lock` respects the request acquire timeout, returns a failed `LockResponse` with a timeout marker, completes quickly, and evicts the cached connection.
- The same pattern verifies `acquire_locks_batch` respects the derived batch timeout, returns one failed response for one request, and evicts the cached connection.
- A unit test verifies `rpc_timeout(Duration::ZERO)` is clamped to 1 ms and nonzero durations are preserved.

These tests directly cover the highest-risk remote acquisition path. There are no local tests for release, refresh, force-release, status approximation, stats, or ping behavior in this file.
