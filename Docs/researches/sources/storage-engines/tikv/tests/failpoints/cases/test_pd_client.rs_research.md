# sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client.rs

## Purpose
This file tests the v2 PD RPC client under reconnect pauses, shared gRPC environment contention, request timeout/backoff, retry behavior, and service GC safe point monotonicity.

## Important APIs, Types, and Functions
- `new_test_server_and_client` creates a mock PD server and `RpcClientV2`.
- The `request!` macro wraps both sync and async PD client methods for deadlock testing.
- `run_on_bad_connection` resets the client to a lame connection and forces reconnect behavior.
- Main APIs under test include `reconnect`, `fetch_cluster_id`, bootstrap/store/region/split/heartbeat/scatter/operator methods, `get_gc_safe_point`, `get_store_and_stats`, and `update_service_safe_point`.

## Control Flow
`test_pd_client_deadlock` pauses `pd_client_reconnect`, then invokes each public client method from a spawned thread and ensures it completes once reconnect resumes. `test_slow_periodical_update` creates two clients sharing one gRPC environment and proves a paused periodical leader update in one client does not block `alloc_id` in another. `test_backoff` simulates short timeouts and longer backoff so the second bad request hits backoff and later succeeds. `test_retry` disables backoff and verifies retry success across many PD methods. `test_update_service_gc_safe_point` updates, rejects unsafe regressions, clears, and updates service safe points.

## State and Persistence Behavior
The client state under test includes leader connection state, initialized/lame connection status, reconnect backoff timers, timeout handling, and in-memory service safe point minimum tracking from mock PD responses. There is no TiKV storage persistence in this file.

## Dependencies and Integration Points
The file uses `test_pd` mock server/service, `grpcio::EnvBuilder`, `SecurityManager`, futures `block_on`, PD proto request/response types, and `TimeStamp`.

## Risks and Test Signals
Risks include client-wide deadlocks during reconnect, shared gRPC CQ starvation, retry loops that do not recover, excessive reconnect attempts, and accepting lower service GC safe points. Signals are `recv_timeout` completion, expected `unwrap_err` on bad connection, later `unwrap` success, and exact `UnsafeServiceGcSafePoint` fields.
