# sources/storage-engines/foundationdb/fdbserver/core/CoordinatedState.cpp

## Purpose
Implements quorum-backed coordinated state on top of generation registers, plus movable coordinated state for coordinator changes. It provides read, conflict monitoring, exclusive write, and coordinated-state migration semantics.

## Important APIs, Types, and Functions
- `waitAndSendRead()` and `waitAndSendWrite()` send generation-register RPCs, optionally through hostname retry paths, with simulation buggified delays.
- `CoordinatedStateImpl::read()`, `onConflict()`, and `setExclusive()` implement the public `CoordinatedState` lifecycle.
- `replicatedRead()` and `replicatedWrite()` issue requests to all state servers and wait for quorum responses.
- `MovableValue` encodes `MaybeTo`, `Active`, and `MovingFrom` states.
- `MovableCoordinatedStateImpl::read()`, `setExclusive()`, `move()`, and `moveTo()` manage quorum-change handoff.
- `updateCCSInMovableValue()` rewrites a connection string embedded in a serialized movable value.

## Control Flow
`CoordinatedState::read()` first reads with generation zero to discover current generations, chooses a new unique generation above conflicts, then reads again at that generation to lock in read intent and retrieve the value. `setExclusive()` writes with that generation and throws `coordinated_state_conflict()` if any replica reports a higher generation. `onConflict()` polls for later generations while the state remains usable.

`replicatedRead()` races a majority of non-empty replies against enough empty replies to prove a majority non-empty cannot be achieved, then returns the best reply by write/read generation. `replicatedWrite()` requires all replicas for initial creation and majority for later writes.

Movable state writes an `Active` encoded value normally. During move, it verifies new coordinators are empty, writes `MovingFrom` to new coordinators, confirms old state was not concurrently changed, writes `MaybeTo` to old state, asks leaders to change coordinators, and throws `coordinators_changed()`.

## State and Persistence Behavior
Durable state is stored in coordinator generation registers under the cluster key. `MovableValue` serialization is protocol-version gated. In-memory state tracks stage, selected generation, conflict generation, doomed flag, initial flag, and outstanding actor collection. Migration persists transitional values to old and new coordinator quorums.

## Dependencies and Integration Points
Depends on cluster connection records, coordination interfaces, leader election coordinator-change support, Flow actor utilities, and server knobs. It is a central dependency for cluster controller leadership and quorum-change workflows.

## Risks and Edge Cases
Initial writes require all replicas, making coordinator creation stricter than normal writes. The read algorithm distinguishes empty and non-empty quorums to preserve consistency under partial initialization. Movable-state migration has several conflict and timeout paths and relies on the new coordinator set being uninitialized. `updateCCSInMovableValue()` assumes the input is a versioned `MovableValue`.

## Test Signals
No embedded tests in this file. Coverage should come from coordinator quorum, cluster-file change, coordinator move, conflict, and simulation buggification tests.
