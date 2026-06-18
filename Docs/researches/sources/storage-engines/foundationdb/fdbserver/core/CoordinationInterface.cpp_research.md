# sources/storage-engines/foundationdb/fdbserver/core/CoordinationInterface.cpp

## Purpose
Constructs coordination RPC interface objects for remote and local use. It binds generation-register, leader-election, and server-coordinator endpoint sets to well-known tokens and task priorities.

## Important APIs, Types, and Functions
- `GenerationRegInterface(NetworkAddress)` creates remote read/write endpoints.
- `GenerationRegInterface(INetwork*)` creates local well-known read/write endpoints at coordination priority.
- `LeaderElectionRegInterface(NetworkAddress)` creates remote leader-election endpoints and inherits client leader endpoints.
- `LeaderElectionRegInterface(INetwork*)` creates local candidacy, election-result, heartbeat, and forward endpoints.
- `ServerCoordinators(ccr)` expands a cluster connection string into leader-election and state-server interfaces for hostnames and coordinator addresses.

## Control Flow
Constructors either wrap remote well-known endpoints from addresses or allocate local well-known endpoints on the current network. `ServerCoordinators` reads hostnames and coordinator network addresses from the connection string and appends matching interface instances to leader and state vectors.

## State and Persistence Behavior
No durable state. Interface objects contain endpoint metadata and optional hostname information used by retry paths.

## Dependencies and Integration Points
Depends on `CoordinationInterface.h`, endpoint well-known tokens, `TaskPriority::Coordination`, and cluster connection records. Used by coordinator servers, coordinated state, leader election, and clients that contact coordinators.

## Risks and Edge Cases
Endpoint token compatibility is critical; changing token bindings breaks wire compatibility between clients and coordinators. Hostname-backed and address-backed paths must remain consistent because callers choose retry behavior based on `hostname.present()`.

## Test Signals
Covered by link tests and by any coordinator/leader-election simulation. Direct tests should verify well-known token assignment and that `ServerCoordinators` preserves connection-string hostnames and addresses.
