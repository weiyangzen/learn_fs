# sources/storage-engines/foundationdb/fdbserver/clustercontroller/include/fdbserver/clustercontroller/ClusterController.h

## Purpose
`ClusterController.h` declares the cluster-controller actor entry point. The cluster controller coordinates cluster leadership/identity state and exposes the full cluster-controller interface through async variables consumed elsewhere in the server.

## Important APIs, Types, and Functions
- Forward declaration `struct ClusterControllerFullInterface` avoids including the full interface definition in this public header.
- `clusterController(...)` returns `Future<Void>` and accepts the cluster connection record, an async variable for the current cluster-controller interface, an async variable for priority information, locality data for the process, and an async variable for the optional cluster ID.

## Control Flow
This header does not implement behavior. It establishes that the cluster controller is a long-running Flow actor. The actor receives shared references to mutable async state, updates those variables as leadership or metadata changes, and completes only on shutdown or error.

## State and Persistence Behavior
The declaration exposes no persistent state directly. The parameters identify the state channels the implementation owns or updates: the durable/coordination-backed cluster connection record, published current cluster-controller interface, priority info, process locality, and optional cluster ID.

## Dependencies and Integration Points
The header depends on `IClusterConnectionRecord`, FDB types, locality data, and Flow futures/async variables. It is included by server startup and cluster-controller implementation code that needs to spawn or refer to the cluster-controller actor without depending on the full implementation internals.

## Risks and Edge Cases
The API relies on shared `Reference<AsyncVar<...>>` objects; consumers can observe transitions, empty optionals, or stale values depending on actor timing. Forward-declaring `ClusterControllerFullInterface` keeps compile dependencies light but requires any user that dereferences the interface contents to include the full definition elsewhere. The actor signature includes both connection-record and cluster-ID state, so mismatches between persisted coordination state and published async variables are important integration risks handled by the implementation, not by this header.

## Test Signals
Build and link coverage are the main direct signals for this header. Runtime signals come from cluster startup/recovery tests that spawn the cluster controller, observe `currentCC`, update priority info, and publish a cluster ID.
