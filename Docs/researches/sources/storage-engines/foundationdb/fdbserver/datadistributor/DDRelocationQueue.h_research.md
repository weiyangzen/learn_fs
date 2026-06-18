# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.h`

## Purpose

This header declares the relocation queue interface, queue data model, throttling helpers, constructor parameter bundle, and `DDQueue` class used by the data distributor to schedule and execute shard relocations. It is the local contract consumed by the actor implementation and by other datadistributor components that need queue status or construction.

## Important APIs and Types

- `IDDRelocationQueue` is the narrow external interface with `getUnhealthyRelocationCount()`.
- `RelocateData` is the queue's normalized relocation intent. It stores the key range, priority decomposition (`priority`, `boundaryPriority`, `healthPriority`), relocation/data-movement reasons, source/destination servers, data-move identity, work factor, trace interval, optional parent split range, optional restored `DataMove`, and optional `DDBulkLoadEngineTask`.
- `RelocateData::isHealthPriority()` and `isBoundaryPriority()` classify server-knob priorities into health and boundary buckets.
- `RelocateDecision` is a trace/reporting view over a relocation, destinations, extra IDs, metrics, and optional parent metrics.
- `Busyness` declares per-priority fixed-point capacity accounting for launch throttling.
- `DDQueueInitParams` groups constructor dependencies: distributor ID, move-keys lock, transaction processor, team collections, failure tracker, physical shard collection, bulk-load collection, average-shard-size stream, team sizes, relocation input/output streams, and metric request streams.
- `DDQueue::DDDataMove` stores a data-move ID plus an optional cleanup future.
- `DDQueue::ServerCounter` tracks proposed/queued/launched source and destination counts per server and `RelocateReason`, with bounded tracing support.
- `DDQueue` exposes state fields and internal methods used by the actor implementation: queueing, launching, validation, source fetch completion, cancellation, counter refresh, rebalance helpers, and static `run()`.

## Control Flow Contract

The header shows the queue's staged model. Relocations enter through `input`, are produced downstream through `output`, and flow through source-fetch queues, per-source queues, in-flight maps, and completion streams. `queueRelocation()` accepts raw `RelocateShard`s and may populate `serversToLaunchFrom`. `completeSourceFetch()` moves source-fetched work into launchable per-server queues. `launchQueuedWork()` overloads support launching by key range, affected source set, or single relocation. `dataTransferComplete` and `relocationComplete` are separate streams because capacity release and full cleanup happen at different times.

## State and Persistence Behavior

The class stores in-memory scheduling state: pipeline counters, active/queued relocation counts, source and destination busyness maps, `queueMap`, `fetchingSourcesQueue`, per-source `queue`, `lastAsSource`, `inFlight`, `inFlightActors`, `dataMoves`, priority counters, unhealthy counts, and moving-window byte rate. Persistent actions are not declared directly here, but the state references the `IDDTxnProcessor`, `MoveKeysLock`, and `DDDataMove` cleanup futures that the implementation uses to mutate location metadata and clean durable data-move state.

## Dependencies and Integration Points

The header depends on `fdbserver/datadistributor/DataDistribution.h` for core DD types (`RelocateShard`, `DataMove`, `TeamCollectionInterface`, `PhysicalShardCollection`, bulk-load types, metric requests) and `MovingWindow.h` for move-rate accounting. `DDQueue` integrates with Flow primitives (`PromiseStream`, `FutureStream`, `AsyncVar`, `FlowLock`, actor maps), team collections for destination selection, failure tracking for shard/team mapping, physical shard collection for physical moves, and bulk-load task collection for range-specific load operations.

## Risks and Edge Cases

Several invariants are visible in the data layout. `noErrorActors` must be destroyed last because other actors may use it. `queueMap`, per-source `queue`, and `fetchingSourcesQueue` must agree on whether a relocation has source servers. `inFlight`, `inFlightActors`, and `dataMoves` must stay range-aligned during cancellation and replacement. `priority_relocations` and `unhealthyRelocations` drive external health signals, so incorrect increments/decrements can block team removal or misreport DD health. `RelocateData` comparison determines set uniqueness through priority/start/random/range ordering; equality is not the set uniqueness predicate.

## Test Signals

The header itself has no tests, but it exposes `ServerCounter::randomCountType()` for the queue unit test in the actor file. Runtime validation is supported by `DDQueue::validate()` under expensive validation, and operational traces are backed by `ServerCounter::traceAll()`, `MovingData`, and physical-shard counter fields.
