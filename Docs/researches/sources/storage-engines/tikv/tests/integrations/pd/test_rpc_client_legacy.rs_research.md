# sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client_legacy.rs

Purpose: validates the legacy `pd_client::RpcClient` API against the same mock PD surface as the v2 suite, preserving compatibility for older synchronous/future-based client methods and callback-style reconnect/heartbeat handling.

Important APIs and functions: tests use `new_client`, `new_client_with_update_interval`, `RpcClient::new`, `get_cluster_id`, `get_tso`, `batch_get_tso`, `handle_region_heartbeat_response`, `region_heartbeat`, `handle_reconnect`, sync/async region and store queries, and `update_service_safe_point`. Shared helper closures `test_retry` and `test_not_retry` assert retryable transport errors are retried while PD error-header responses are not.

Control flow: a mock PD server is started per scenario, the legacy client runs operations through blocking calls or futures driven by `futures::executor::block_on` and a small Tokio poller. Heartbeat tests spawn response handlers and heartbeat futures, then use channels for assertions. Retry tests install mockers that fail a configured fraction of requests. Leader-change tests count reconnect callbacks rather than reading a broadcast receiver.

State and persistence: mock PD state covers cluster bootstrap, stores/regions, tombstone state, leader endpoint, cluster version, and service GC safepoints. Client state includes cached leader, feature gate, reconnect callback list, and heartbeat response handlers.

Dependencies and integration points: uses `pd_client::{PdClient, RpcClient, PdConnector, RegionStat}`, `raftstore::store` constants, `grpcio`, `test_pd`, `security`, Tokio runtime builder, channels, atomics, and `txn_types::TimeStamp`.

Risks: legacy timing constants differ from v2, including sleeps for reconnect intervals. Callback/channel tests can be flaky if runtime scheduling stalls. Stringified gRPC status comparisons are brittle. Service safepoint assertions depend on mock PD faithfully implementing minimum safepoint semantics.

Test signals: successful bootstrap/query/TSO/heartbeat flow, expected retry and non-retry outcomes, callback invocation on leader change, feature-gate monotonicity, correct tombstone and incompatible-version errors, heartbeat recovery after failpoint removal, and `UnsafeServiceGcSafePoint` errors when lowering a service safepoint.
