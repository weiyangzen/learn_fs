# sources/storage-engines/tikv/components/pd_client/src/client_v2.rs

## Purpose
`client_v2.rs` implements a newer PD client architecture where one reconnect loop owns connection maintenance and request users subscribe to published connection changes. It avoids the older design where each request can rebuild shared connection state.

## Important APIs, Types, and Functions
- `ConnectContext` stores immutable config and connector.
- `RawClient` stores a `PdClientStub`, target info, and members; `connect` validates endpoints and `maybe_reconnect` refreshes the connection.
- `CachedRawClient` holds shared latest client state, a local cache, version counters, reconnect request broadcast, and reconnect notifications. Key methods are `wait_for_ready`, `connect`, `reconnect`, `check_resp`, `header`, and `call_option`.
- `reconnect_loop` performs initial connect, waits for readiness/state changes or reconnect requests, backs off, and publishes new clients.
- `RpcClient` wraps `CachedRawClient` plus `FeatureGate`.
- The local v2 `PdClient` trait exposes mutable-client operations and stream creation methods.
- `CachedDuplexResponse` swaps to the latest grpc response receiver when streams reconnect.

## Control Flow
Requests call `wait_for_ready`, fill headers from the current raw client, issue grpcio calls with timeouts, pass errors through `check_resp` to request reconnects, check response headers, and update metrics. Stream creation spawns loops that wait for ready clients, create grpc duplex streams, publish new response receivers, pipe request channels into grpc sinks, and reconnect on stream errors. `select!` is used in reconnect and bucket stream loops to react to either state changes or stream exits.

## State and Persistence Behavior
State is in-memory connection state: cached stubs, PD member metadata, monotonic cache version, reconnect broadcasts, and feature gate cluster version. The client mutates PD cluster state through requests but does not persist locally.

## Dependencies and Integration Points
The file integrates grpcio channel readiness APIs, `tokio::sync::broadcast` and mpsc, futures streams/sinks, global timer compatibility, failpoints, security connector, kvproto PD services, metrics, and `txn_types::TimeStamp`.

## Risks
Correctness depends on monotonically increasing cache versions and publishing only after a real new connection. `wait_for_ready` can time out and request reconnect; callers must handle transient errors. Broadcast channels are size 1, so lagging receivers can miss intermediate events by design. Unbounded request channels are still used for streams. Several stub creation failures panic. The v2 trait is distinct from the public `crate::PdClient`, so integration code must use the correct trait.

## Test Signals
Feature-gated test exports expose initialization, leader lookup, forced reconnect, reset-to-lame-client, and feature gate access. Failpoints control request timeout, reconnect backoff, forced reconnect, and heartbeat send failure.
