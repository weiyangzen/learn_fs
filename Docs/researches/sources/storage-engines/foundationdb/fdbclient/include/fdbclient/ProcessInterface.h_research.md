# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ProcessInterface.h

## Purpose
`ProcessInterface.h` declares RPC message types for retrieving process-level interfaces and actor lineage profiling samples. It gives other components a typed way to ask a process for its actor lineage data over FoundationDB RPC streams.

## Important APIs, Types, And Functions
- `ProcessInterface` contains request streams for `GetProcessInterfaceRequest` and `ActorLineageRequest`. Its serializer currently serializes `actorLineage`.
- `GetProcessInterfaceRequest` carries a `ReplyPromise<ProcessInterface>`.
- `SerializedSample` transports a timestamp and a `std::unordered_map<WaitState, std::string>` of serialized profiling data.
- `ActorLineageReply` wraps a vector of samples.
- `ActorLineageRequest` carries a wait-state range, time range, and reply promise.

## Control Flow And State
Callers send `GetProcessInterfaceRequest` to discover a process interface, then send `ActorLineageRequest` through `actorLineage`. The request filters samples by wait-state start/end and time start/end; the reply returns a batch of serialized samples.

## Persistence And External State
All structures are transient RPC payloads. `constexpr FileIdentifier` values make them part of FDB's typed serialization protocol and must remain compatible across deployments.

## Dependencies And Integration Points
The header depends on actor annotation types, FDB types, fdbrpc streams/promises, and well-known endpoints. It integrates with actor lineage profiling, process discovery, and any special key or status surface that exposes process stack/lineage data.

## Risks And Edge Cases
Changing serialization fields or file identifiers can break wire compatibility. `ProcessInterface::serialize()` only serializes `actorLineage`, so adding streams requires a deliberate protocol update. Time fields use `time_t`, which can vary by platform width. Large sample vectors or maps may create heavy replies.

## Test Signals
Tests should cover serialization round trips across protocol versions, request/reply routing, lineage filtering by time and wait-state, behavior with no samples, and compatibility when process interfaces are fetched from mixed-version processes.
