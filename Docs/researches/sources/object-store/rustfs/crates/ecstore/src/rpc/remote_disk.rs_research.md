# sources/object-store/rustfs/crates/ecstore/src/rpc/remote_disk.rs

## Purpose

`remote_disk.rs` implements the remote-node `DiskAPI` adapter for RustFS erasure-coded storage. A `RemoteDisk` presents a disk-like interface to the rest of `ecstore`, but every operation is executed against another node through either the node-service gRPC API or the configured internode data transport. Small control and metadata operations are mostly unary gRPC calls; data streams for object reads, object writes, and directory walks are delegated to `InternodeDataTransport`.

The file also owns runtime remote-drive health tracking. It converts timeouts and network-like failures into `DiskHealthTracker` state transitions, evicts cached gRPC channels, records metrics, and starts recovery probes that require the remote disk RPC path to be healthy before a disk is restored to online state.

## Important APIs, Types, and Functions

- `RemoteDisk`: stores the local view of a remote disk: optional disk UUID, base node address, full `Endpoint`, scan counter, health-check enablement, shared `DiskHealthTracker`, cancellation token, and `Arc<dyn InternodeDataTransport>`.
- `RemoteDisk::new`: builds the base node address from the endpoint scheme, host, and optional port, applies the `DiskOption` health flag plus `ENV_RUSTFS_DRIVE_ACTIVE_MONITORING`, initializes health state as online, and stores the transport dependency.
- `DiskAPI for RemoteDisk`: maps the disk trait to remote calls. It covers volume lifecycle, metadata reads and writes, object version operations, data file streaming, directory walking, deletes, part checks, bulk reads, whole-file read/write, disk info, disk location, scan tracking, and close.
- `execute_with_timeout`, `execute_with_timeout_for_op`, and `execute_with_timeout_for_op_and_health_action`: centralized operation wrapper that enforces per-operation timeouts, short-circuits faulty disks, tracks in-flight health counters, records timeout/network metrics, evicts failed connections, and optionally ignores failure-induced health transitions for selected operations.
- `FailureHealthAction`: controls whether timeout-like or network-like failures should mark the disk suspect/offline. `walk_dir` uses `IgnoreFailure` to avoid allowing listing stalls to poison the drive health state.
- `monitor_remote_disk_health` and `monitor_remote_disk_recovery`: background tasks that probe connectivity and recovery. Active health checks use a TCP connectivity probe; recovery requires a successful noop `disk_info` gRPC call and evicts stale cached connections on probe failures.
- `open_write_with_retry`: retries `InternodeDataTransport::open_write` once for retryable internode write failures, records retry/success metrics by backend and error classification, and keeps non-retryable errors single-shot.
- `copy_stream_with_buffer`: copies an async reader to an async writer with a configurable buffer and flushes at EOF. It is used for streamed `walk_dir` output.
- `encode_msgpack` and `decode_msgpack_or_json`: compatibility helpers for request/response payloads where newer binary msgpack fields coexist with older JSON string fields.

## Control Flow

Construction records the remote disk as online, keeps the endpoint path for disk identity, and keeps the node base address for gRPC channel lookup. `disk_ref()` returns the disk UUID once set, otherwise it falls back to the endpoint string. Many RPCs that can address disks by durable UUID call `disk_ref()`, while older or endpoint-shaped APIs still pass `self.endpoint.to_string()`.

Most unary methods follow a common sequence:

1. Log a structured `remote_disk_rpc` start event with endpoint, operation name, and relevant volume/path fields.
2. Serialize request data, often JSON plus msgpack when the protobuf has binary compatibility fields.
3. Call `execute_with_timeout*` with an operation-specific timeout from `disk_store` configuration.
4. Get a signed tonic node-service client through `node_service_time_out_client` and `gen_tonic_signature_interceptor`.
5. Build a protobuf request, call the matching node-service RPC, check `response.success`, convert `response.error` to `DiskError` when needed, and decode the success payload.

Volume methods (`make_volume`, `make_volumes`, `list_volumes`, `stat_volume`, `delete_volume`) use node-service protobufs and JSON `VolumeInfo` decoding. Metadata and version methods (`write_metadata`, `read_metadata`, `update_metadata`, `read_version`, `read_xl`, `rename_data`) serialize `FileInfo`, `RawFileInfo`, `ReadOptions`, and update options, preferring msgpack response fields when present. Delete methods include single-version delete, batch version delete, delete paths, and generic delete; the batch version path returns a `Vec<Option<Error>>` instead of a single `Result` and manually fans out serialization/RPC errors across all requested versions.

Stream-oriented data operations bypass unary gRPC payloads:

- `read_file` delegates to `read_file_stream`.
- `read_file_stream` checks the health state, resolves `disk_ref()`, and calls `data_transport.open_read` with endpoint grid host, disk, volume, path, offset, and length.
- `read_file_zero_copy` cannot truly zero-copy across the network, so it reads a stream into one `Vec` allocation and returns `Bytes`.
- `append_file` and `create_file` check health, resolve disk, then call `open_write_with_retry` with append flag and expected size.
- `walk_dir` serializes `WalkDirOptions` to JSON, sets a stall timeout, optionally disables the total timeout via `skip_total_timeout`, opens a walk stream through `data_transport.open_walk_dir`, and copies stream bytes into the caller-provided writer. It retries only if opening the stream fails with a retryable transport/decoding error; it does not retry after partial bytes have already been written.

Health control flow is layered. `is_online` is a local health-state check, not an active network ping. `enable_health_check` spawns active monitoring only if remote active monitoring is enabled. `monitor_remote_disk_health` starts with a TCP probe, periodically probes again after the recent-success grace window, marks failures through `DiskHealthTracker`, and starts recovery monitoring after a transition. `monitor_remote_disk_recovery` loops until a noop `disk_info` RPC succeeds and `mark_recovery_success` returns the disk to online, or until the cancellation token is cancelled. `close` cancels these monitor tasks.

## State and Persistence Behavior

The file does not persist data locally. It is an RPC facade over remote disk persistence owned by the peer node. Its local state is runtime-only:

- `id: Mutex<Option<Uuid>>` is mutable in-memory disk identity. Setting it changes future `disk_ref()` addressing for UUID-aware RPCs and transports.
- `DiskHealthTracker` stores runtime health state, failure/recovery timestamps, waiting counters, last start/success times, and capacity snapshots.
- `scanning: Arc<AtomicU32>` tracks active scans through `start_scan()` and `ScanGuard`.
- `cancel_token` coordinates shutdown of health/recovery monitor tasks.
- gRPC channels are cached outside this struct by the shared connection map behind `node_service_time_out_client`; this file evicts them with `evict_failed_connection` after timeout/network failures.

Remote persistence is affected by the API calls themselves: metadata writes update xl/file metadata on the remote disk, creates/appends stream object data to the remote disk, rename/delete calls mutate object paths and versions, and `disk_info` reads remote state. Serialization compatibility is important because binary msgpack fields and JSON fallback fields may coexist across mixed versions.

## Dependencies and Integration Points

Key internal dependencies include:

- `crate::disk::*`: the `DiskAPI` trait, disk error/result types, file readers/writers, option structs, volume and disk info types, `DiskHealthTracker`, `RuntimeDriveHealthState`, and timeout/environment helpers.
- `crate::rpc::client`: signed tonic interceptor creation, node-service client creation, and network-like disk error classification.
- `crate::rpc::internode_data_transport`: transport trait plus read/write/walk request shapes used for high-volume streams.
- `rustfs_protos`: node-service protobuf request/client types and cached connection eviction.
- `rustfs_filemeta`: `FileInfo`, `RawFileInfo`, and `ObjectPartInfo` payload models.
- `rustfs_io_metrics` and `metrics`: internode gRPC/TCP metrics, retry counters, timeout counters, byte counters, and failure counters.
- `tokio`, `tonic`, `bytes`, `serde_json`, `rmp-serde`, `tracing`, and `uuid`: async execution, gRPC, payload buffers, serialization, structured logs, and disk IDs.

The adapter integrates with erasure-set code wherever a `DiskAPI` object is expected. It also integrates with the node-service server contract: every protobuf request field and success/error convention here must match the server implementation. The stream methods integrate with the configured internode transport backend, currently tested with a TCP/HTTP capability shape. Runtime health integrates with cluster drive-state reporting through `record_drive_runtime_state` and `DiskHealthTracker`.

## Risks and Edge Cases

- Mixed disk addressing is a compatibility risk. Some methods send `disk_ref()` while others still send `endpoint.to_string()`. Server-side expectations must remain compatible when disk IDs are set.
- `Duration::ZERO` disables total operation timeout in `execute_with_timeout`; methods using it can wait indefinitely unless the underlying client or transport enforces its own deadline.
- `list_volumes`, `read_multiple`, and other collection decoders use `filter_map(...ok())` in places, silently dropping malformed entries rather than returning an error. That can hide partial decode failures.
- `delete_versions` is less uniform than most methods: it creates the client before entering `execute_with_timeout`, manually converts many errors into repeated per-version errors, and converts server error strings with limited structure.
- `walk_dir` intentionally ignores health marking for total/stall failures. This avoids false drive-offline transitions for listing streams, but it means repeated listing transport failures may not influence disk health.
- Retrying `walk_dir` is safe only before bytes are copied. A failure after partial output returns an I/O error and leaves the caller with partial data already written.
- Health probes use TCP for active monitoring and gRPC `disk_info` for recovery. This is stricter on recovery, but initial TCP success alone does not prove disk RPC readiness.
- Background monitor spawning is edge-triggered by health transitions. Repeated transitions could create multiple monitor tasks if tracker semantics change.
- `read_file_zero_copy` reserves `length` capacity. Very large or untrusted lengths can increase memory pressure.
- Serialization compatibility depends on both JSON and msgpack schemas remaining aligned across nodes.

## Test Signals

The in-file tests are broad and focused on adapter reliability:

- Construction/property tests verify endpoint parsing, host names, path extraction, disk location conversion, local/remote flags, disk ID set/get, `disk_ref()` UUID preference, and close cancellation.
- Health tests cover online behavior, missing listeners moving runtime state away from online, first timeout/network errors moving to suspect rather than immediate offline, ignored failure actions preserving online state, business errors not poisoning health, and cached connection eviction on timeout/network-like errors.
- Recovery tests verify that a plain TCP listener is insufficient for recovery; successful recovery requires disk RPC readiness through `disk_info`, and failed probes evict stale channels.
- Transport tests verify that read, create, append, and walk operations use the configured `InternodeDataTransport` with expected endpoint, disk, path, size, body, and stall timeout fields.
- Retry tests cover one retry for retryable open-write errors, no retry for non-retryable write errors, one retry for retryable walk open errors, and no retry after partial walk output.
- Observability tests verify recovery-monitor spans preserve request context and that network-error-triggered recovery monitor logs include both request and recovery span context.

These tests exercise the highest-risk behavior without needing a real remote node by using mock transports, hanging listeners, captured logs, and the global cached connection map.
