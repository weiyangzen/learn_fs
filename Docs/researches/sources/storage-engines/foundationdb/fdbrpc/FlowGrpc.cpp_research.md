# sources/storage-engines/foundationdb/fdbrpc/FlowGrpc.cpp

## Purpose
`FlowGrpc.cpp` implements fdbrpc's optional gRPC runtime initialization and `GrpcServer` lifecycle management.

## Important APIs, Types, and Functions
Important functions include `FlowGrpc::init`, `GrpcServer` constructor/destructor, `GrpcServer::run`, `runInternal`, `shutdown`, `stopServer`, `stopServerSync`, `stopServerSyncInternal`, `registerService`, `registerRoleServices`, `deregisterRoleServices`, and `deregisterRoleServicesSync`.

## Control Flow
`FlowGrpc::init` installs a global `FlowGrpc` state object, chooses insecure or TLS credential provider, and optionally creates a server. `GrpcServer::run` awaits `runInternal` and shuts down unless already shutdown. `runInternal` waits until services are registered, stops any existing server, builds a new `grpc::ServerBuilder`, registers all service instances, starts the server, increments start count, triggers start waiters, and then waits for service-list changes to restart. Deregistration stops the current server, removes services by owner UID, and triggers a rebuild.

## State and Persistence Behavior
Runtime state includes global `FlowGrpc`, credential provider, optional server, registered service map keyed by owner `UID`, server pointer, lifecycle state enum, start count, trigger variables, an async task executor pool, and the server actor future. No application data is persisted.

## Dependencies and Integration Points
It depends on `fdbrpc/FlowGrpc.h`, Flow errors/tracing/network globals, gRPC server builder, credential providers, `AsyncTaskExecutor`, and TLS config. It integrates gRPC services into Flow's actor lifecycle and network-global storage.

## Risks and Edge Cases
`stopServerSyncInternal` appears to have an inverted null check: it returns when `server_ != nullptr` and otherwise dereferences `server_`, which would prevent shutdown of a live server and crash on null if reached. `deregisterRoleServicesSync` calls the internal stop function directly, so it inherits that risk. Service registration with `registerService` uses a fresh random UID that cannot be deregistered by caller. Restarting the entire gRPC server for service changes can interrupt in-flight RPCs.

## Test Signals
`FlowGrpcTests.actor.cpp` and `FlowGrpcTests.cpp` test basic server/client RPCs, stream reads, no-server failure, destructor cleanup, lifecycle restart behavior, and TLS credential behavior under `FLOW_GRPC_ENABLED`.
