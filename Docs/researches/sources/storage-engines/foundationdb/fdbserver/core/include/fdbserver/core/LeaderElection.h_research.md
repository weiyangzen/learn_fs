# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LeaderElection.h

## Purpose
`LeaderElection.h` declares the coordinator-backed sticky leader election API used by cluster controllers and other leader-like server components.

## Important APIs, Types, And Functions
The template `tryBecomeLeader` accepts `ServerCoordinators`, a proposed local leader interface, an `AsyncVar<Optional<LeaderInterface>>` for the best known leader, connection state, and priority info. `tryBecomeLeaderInternal` handles serialized values. `changeLeaderCoordinators` forwards coordinator replacement information.

## Control Flow
The template serializes the proposed interface with `ObjectWriter::toValue(..., IncludeVersion())`, starts the internal election actor, and races/combines it with `asyncDeserialize` to keep the typed `outKnownLeader` updated. If the local proposal becomes leader, the known leader reflects that interface until displaced or cancelled.

## State And Persistence Behavior
Leader state is stored through the coordination service, not this header. The local output is transient `AsyncVar` state. Serialization versioning matters because coordinator values can outlive a process.

## Dependencies And Integration Points
It depends on `fdbrpc`, locality, FDB types, `ServerCoordinators`, `ClusterControllerPriorityInfo`, object serialization, and async deserialization. It integrates with cluster-controller candidacy and coordinator change workflows.

## Risks And Edge Cases
The main risks are stale serialized leader interfaces, cancellation semantics, priority/fitness races, and cross-version compatibility of leader interface serialization. Sticky leadership can mask degraded leaders until communication failures are detected.

## Test Signals
Simulation tests should show one active leader, stable leadership through benign coordinator polling, displacement when a better/new leader wins, correct cancellation cleanup, and correct behavior after coordinator connection string changes.
