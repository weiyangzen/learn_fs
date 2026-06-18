# sources/object-store/rustfs/crates/common/src/globals.rs

## Purpose
`globals.rs` provides process-global RustFS node settings and caches, including local node name, host/port/address, gRPC connection cache, TLS root certificate, outbound mTLS identity, TLS generation, and node initialization time.

## Important APIs, Types, and Functions
Global statics use `LazyLock<RwLock<...>>` for strings, optional cert/identity, connection map, and init time, plus `AtomicU64` for outbound TLS generation. Public setters/getters include `set_global_local_node_name`, `get_global_local_node_name`, `set_global_init_time_now`, `get_global_init_time`, `set_global_addr`, `set_global_root_cert`, `set_global_mtls_identity`, `set_global_outbound_tls_generation`, and `get_global_outbound_tls_generation`. Connection cache helpers are `evict_connection`, `has_cached_connection`, and `clear_all_connections`. `MtlsIdentityPem` stores cert and key PEM bytes.

## Control Flow
Setters acquire write locks and replace values. Getters acquire read locks and clone/copy values. Connection eviction removes one channel and logs if present. Clearing removes all cached channels and warns when anything was cleared. TLS generation uses relaxed atomic store/load.

## State and Persistence Behavior
All state is process-global and in-memory. There is no reset-all helper for every global; connection cache can be cleared explicitly. `GLOBAL_INIT_TIME` is optional until set. `GLOBAL_CONN_MAP` stores `tonic::transport::Channel` values by address.

## Dependencies and Integration Points
The file integrates with Tokio async synchronization, Tonic gRPC clients, Chrono UTC timestamps, and tracing. It is re-exported by `common/src/lib.rs`, making these globals part of the common crate public surface.

## Risks and Edge Cases
Global mutable state can create test ordering and multi-tenant issues. `set_global_root_cert` only sets `Some(cert)` and has no public clear function, while mTLS identity can be set to `None`. Relaxed ordering for TLS generation is enough for a simple version counter only if callers do not rely on memory synchronization. Connection cache invalidation must be called on node failure or TLS config changes to avoid stale channels.

## Test Signals
No tests are in this file. Expected behavior is inferred from simple setters/getters and logging on cache eviction/clear.
