# sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.h

## Purpose
Declares the GRV proxy health metrics cache/server.

## Important APIs, Types, and Functions
- `HealthMetricsRequestServer` owns a proxy interface plus normal and detailed cached replies.
- `update(...)` refreshes cached replies.
- `run()` serves the request stream.

## Control Flow
Constructed by `grvProxyServerCore`, updated by ratekeeper polling, and run as an actor.

## State and Persistence Behavior
Stores only in-memory cached replies.

## Dependencies and Integration Points
Includes `fdbclient/GrvProxyInterface.h` and Flow. Private to the GRV proxy component.

## Risks and Edge Cases
Normal and detailed metrics have different freshness. No explicit synchronization is needed under Flow actor scheduling.

## Test Signals
No direct tests in this subset.
