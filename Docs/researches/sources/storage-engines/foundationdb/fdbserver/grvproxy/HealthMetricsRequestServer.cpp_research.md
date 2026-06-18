# sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.cpp

## Purpose
Implements a cached GRV proxy health metrics request server backed by ratekeeper updates.

## Important APIs, Types, and Functions
- Constructor stores the `GrvProxyInterface`.
- `update(HealthMetrics const&, bool detailed)` merges metrics into normal and optionally detailed cached replies.
- `run()` serves `grvProxy.getHealthMetrics` forever and sends normal or detailed cached replies.

## Control Flow
`getRate` updates the server when ratekeeper replies arrive. `grvProxyServerCore` runs `run()` as a long-lived actor. Requests are answered from cache rather than synchronously contacting ratekeeper.

## State and Persistence Behavior
Maintains in-memory normal and detailed `GetHealthMetricsReply` snapshots. No persistence.

## Dependencies and Integration Points
Depends on `GrvProxyInterface`, `GetHealthMetricsRequest`, `GetHealthMetricsReply`, and ratekeeper `HealthMetrics`. Integrated by `GrvProxyServer.cpp`.

## Risks and Edge Cases
Before the first update, replies are default-constructed. Detailed snapshots can be older than normal snapshots because they update only on detailed ratekeeper replies.

## Test Signals
No direct tests in this subset; exercised through GRV proxy health metric request paths.
