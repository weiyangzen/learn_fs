# sources/storage-engines/tikv/components/cdc/tests/mod.rs

## Purpose
This module is the shared harness for CDC integration tests. It wires CDC endpoints into simulated TiKV server clusters, exposes helpers for opening CDC event streams, and wraps common transactional/raw KV RPCs with assertions so integration tests can focus on event expectations.

## Important APIs, Types, And Functions
`init` runs CI test setup once. `ClientReceiver` wraps an optional `ClientDuplexReceiver<ChangeDataEvent>` in `Arc<Mutex<...>>` and allows tests to swap or drop streams with `replace`. `new_event_feed` opens the classic CDC duplex stream and `new_event_feed_v2` opens stream multiplexing by attaching the `features: stream-multiplexing` metadata header. Both delegate to `create_event_feed`, which returns a request sender, a `ClientReceiver`, and a `receive_event` closure that polls with `cdc::recv_timeout`, skips resolved-ts events unless requested, and restores the receiver into the mutex.

`TestSuiteBuilder` owns optional `Cluster<ServerCluster>` and memory quota settings. Its `build_with_cluster_runner` installs CDC gRPC services, txn-extra schedulers, CDC observers, memory quotas, endpoint workers, raft routers, local tablet handles, concurrency managers, and causal timestamp providers for every store. `TestSuite` exposes the built cluster, endpoint workers, observers, clients, concurrency managers, and a gRPC environment.

The helper methods include `new_changedata_request`, `must_kv_prewrite`, `must_kv_prewrite_with_source`, `must_kv_put`, `must_kv_compare_and_swap`, `must_kv_compare_and_delete`, `must_kv_commit`, `must_kv_commit_with_source`, `must_kv_rollback`, `must_check_txn_status`, pessimistic lock/prewrite/rollback helpers, `must_kv_txn_heartbeat`, async commit helpers, client lookup helpers, region context helpers, TSO/causal timestamp helpers, and flashback helpers.

## Control Flow
The builder creates one lazy CDC worker per simulated store before the cluster is run. It registers a closure in `pending_services` so each server exposes `create_change_data(cdc::Service::new(...))`, installs `CdcTxnExtraScheduler` into simulated transaction schedulers, and registers `CdcObserver` with each coprocessor host. After the cluster runner starts the cluster, it constructs `cdc::Endpoint` values with the default cluster ID, CDC/resolved-ts config, API version, PD client, raft router, local tablet, observer, store metadata, concurrency manager, security manager, memory quota, and causal-ts provider. It applies a smaller `min_ts_interval` and scan batch size for deterministic tests, then starts each endpoint worker.

The receive closure temporarily takes ownership of the gRPC receiver so only one read happens at a time. If resolved-ts filtering is disabled, it loops past resolved-ts messages until a non-resolved event is found or the stream times out.

## State And Persistence Behavior
The harness itself does not implement persistence, but all helper RPCs mutate the cluster's real test engines and assert there are no region or key errors. It stores runtime state for CDC endpoint workers, observers, per-store memory quotas, client caches, concurrency managers, and the event receiver wrapper. `stop` drains and stops endpoint workers before shutting down the cluster to avoid leaked worker threads.

## Dependencies And Integration Points
This module bridges CDC, raftstore, TiKV storage config, gRPC, PD, concurrency manager, causal timestamp, and test utilities. It depends on `OnlineConfig` behavior for config diffs, `LocalTablets::Singleton` for engine binding, `CdcRaftRouter` for raft messages, and protobuf clients for both CDC and TiKV KV APIs. Tests integrate with it through public helpers rather than constructing CDC endpoints directly.

## Risks
The harness is intentionally opinionated: it forces `min_ts_interval` to 100 ms and max scan batch size to 2, which many tests rely on. Changes here can ripple through event batching and resolved-ts assertions across the integration suite. The `receive_event` closure returns a default event on timeout or after receiver removal, so callers must distinguish default events from legitimate empty responses. The builder assumes simulated node IDs are `1..=count`.

## Test Signals
This module is exercised by every CDC integration test in the directory. Its assertions catch failed KV RPCs immediately, and its endpoint validation hooks give tests direct visibility into CDC delegates, old-value cache counters, and worker lifecycle.
