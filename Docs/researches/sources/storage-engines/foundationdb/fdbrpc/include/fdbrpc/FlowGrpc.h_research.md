# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowGrpc.h

## Purpose
`FlowGrpc.h` declares optional gRPC backend globals and server management for FoundationDB when `FLOW_GRPC_ENABLED` is defined.

## Important APIs, Types, and Functions
`FlowGrpc` provides singleton access through `g_network` globals, `init`, `server`, `serverCreds`, and `clientCreds`. `GrpcServer` declares service registration, role-owned service registration/deregistration, `run`, `stopServer`, `shutdown`, `onRunning`, `onNextStart`, `onStop`, TLS checks, `hasStarted`, and test counter `numStarts`.

## Control Flow
`FlowGrpc::init` configures credentials and optionally creates a server for a local address. `GrpcServer::run` starts a server and returns a future that completes after shutdown; service-list changes trigger restarts after a short debounce. Workers register services under their UID and deregister them on restart or termination.

## State and Persistence Behavior
State is process-global through `g_network->global(INetwork::enGrpcState)`. `GrpcServer` stores address, async task executor, run actor, triggers, registered service map, underlying `grpc::Server`, credential provider, state enum, and start count. No durable state is stored.

## Dependencies and Integration Points
It depends on Flow futures/network/TLS, gRPC service/server types, async gRPC client/task executor, and credential providers. It integrates with worker roles that expose gRPC services and with TLS configuration refresh.

## Risks and Edge Cases
The entire header is conditional; callers must guard usage when gRPC is disabled. Server restart on service change can disrupt active clients. Stop methods may block synchronously in destructors or sync variants. Service ownership is by UID, so stale or reused IDs can affect deregistration behavior.

## Test Signals
Signals include server start count, `onRunning`/`onStop` futures, TLS-enabled checks, successful service registration/deregistration, and client calls against registered services in gRPC-enabled builds.
