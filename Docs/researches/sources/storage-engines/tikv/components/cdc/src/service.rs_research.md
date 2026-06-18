# sources/storage-engines/tikv/components/cdc/src/service.rs

## Purpose
`service.rs` is the gRPC front end for the CDC `ChangeData` service. It accepts client event-feed streams, creates CDC connection state, parses version/features, converts register/deregister requests into endpoint tasks, and forwards endpoint events back to the gRPC sink.

## Important APIs, Types, and Functions
- `validate_kv_api` permits TiDB API and RawKV only when TiKV runs API V2.
- `RequestId` identifies logical subscriptions within a connection.
- `FeatureGate` models version-default and explicitly requested features: batch resolved-ts, cluster-id validation, and stream multiplexing.
- `Conn` tracks `ConnId`, sink, peer, negotiated version/features, and `(request_id, region_id) -> DownstreamValue`.
- `EventFeedHeaders` parses `features` request metadata for `event_feed_v2`.
- `Service::handle_event_feed` is the central stream lifecycle function.
- `handle_register` creates `ObservedRange` and `Downstream`; `handle_deregister` maps region/request scope to endpoint deregistration variants.

## Control Flow
`event_feed` and `event_feed_v2` call `handle_event_feed`; v2 first validates feature headers and fails the RPC with `UNIMPLEMENTED` for unknown features. A fresh `ConnId`, bounded CDC channel, and `Conn` are created, then `Task::OpenConn` is scheduled. The receive future reads the first request to parse TiCDC version, schedules `SetConnVersion`, handles that request, and then handles the rest. A watchdog is spawned. Separate receive and send tasks race normal stream completion against watchdog abort signals; receive-side closure deregisters the connection, while send-side failure fails the gRPC sink.

## State and Persistence Behavior
Connection and downstream maps are in-memory endpoint state. `ConnId` is process-local. No persistent state is written; registration durability is provided by clients re-registering streams. The service shares the CDC `MemoryQuota` with channel/backpressure and watchdog decisions.

## Dependencies and Integration Points
The file integrates grpcio generated `ChangeData`, CDC channel `Sink`, endpoint `Task`, delegate `Downstream`, watchdog, memory quota, and kvproto change-data request/response messages. It is the external API boundary for TiCDC and RawKV CDC clients.

## Risks and Edge Cases
`Conn::features` unwraps, so the endpoint must set version before feature checks. Duplicate `(request_id, region_id)` subscriptions return the previous downstream instead of replacing it. Header parsing rejects unknown explicit features. Send and receive tasks both can deregister on abort/failure, so endpoint deregistration must be idempotent.

## Test Signals
Unit tests cover gRPC flow control and watchdog idle timeout behavior. Failpoint integration tests elsewhere exercise stream multiplexing, register/deregister races, RawKV resolved-ts behavior, and connection failure paths.
