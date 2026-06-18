# sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client_legacy.rs

## Purpose
This file provides equivalent failpoint coverage for the legacy `RpcClient`, focusing on reconnect deadlocks, slow periodical PD leader updates, and reconnect rate limiting.

## Important APIs, Types, and Functions
- `new_test_server_and_client` constructs a mock PD server and legacy client.
- The `request!` macro wraps legacy `PdClient` APIs including async region info, region heartbeat, split, store heartbeat, GC safe point, store stats, operator, and TSO calls.
- `handle_reconnect` is used in the deadlock test to force only one reconnect step per request.

## Control Flow
`test_pd_client_deadlock` wraps the client in `Arc`, pauses `pd_client_reconnect`, launches each PD method in a spawned thread, uses `handle_reconnect` to return from the reconnect failpoint once, removes the pause, and expects method completion within 500 ms. `test_slow_periodical_update` mirrors the v2 test with two clients sharing one gRPC environment. `test_reconnect_limit` waits beyond the default retry interval, allows one reconnect, then asserts subsequent reconnect calls are canceled by the speed limit.

## State and Persistence Behavior
The state is client-side reconnect scheduling, last-update tracking, and shared environment behavior. No raftstore or RocksDB state is created.

## Dependencies and Integration Points
The test uses `test_pd` mock server/service, legacy `RpcClient`, `PdClient`, `RegionInfo`, `RegionStat`, `grpcio::EnvBuilder`, and `SecurityManager`.

## Risks and Test Signals
Risks include legacy client methods blocking behind reconnect, one client's periodical update blocking another client's RPC, or reconnect storming. Signals are spawned-thread timeout checks and errors containing `cancel reconnection`.
