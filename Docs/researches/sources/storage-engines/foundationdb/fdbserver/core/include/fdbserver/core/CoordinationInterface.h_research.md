# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinationInterface.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinationInterface.h

Purpose: defines server-side coordination and leader-election RPC interfaces, request/reply payloads, and coordinator collections.

Important APIs/types: `GenerationRegInterface`, `UniqueGeneration`, `GenerationRegReadReply`, `GenerationRegReadRequest`, `GenerationRegWriteRequest`, `LeaderElectionRegInterface`, `CandidacyRequest`, `ElectionResultRequest`, `LeaderHeartbeatReply`, `LeaderHeartbeatRequest`, `ForwardRequest`, `ServerCoordinators`, and `updateCCSInMovableValue`.

Control flow and state: generation registry reads/writes carry a key and `UniqueGeneration`; comments define total ordering semantics for read/write pairs. `UniqueGeneration` compares first by generation then UID and serializes both. Leader election extends the client leader registration interface with candidacy, election result, heartbeat, and forward streams. Election and heartbeat requests carry leader info, known leader/change IDs, coordinator host/address lists, and reply promises. Forward requests carry a cluster connection string value for movable-state handoff.

State and persistence behavior: these are wire contracts for coordination state and leader election. File identifiers and serialization fields must remain compatible across processes and versions.

Dependencies and integration: depends on client coordination interfaces and well-known endpoints. `ServerCoordinators` wraps client coordinators with server leader-election and generation-reg interfaces. Coordinated state and cluster controller election paths consume these messages.

Risks and tests: comment notes a specification bug around returned read generation after no prior write/data loss. Serialization ordering, host/address compatibility, and forwarding of movable connection strings are sensitive. Tests should cover generation ordering, stale leader heartbeat, candidacy races, hostname and address coordinator forms, and `updateCCSInMovableValue`.
