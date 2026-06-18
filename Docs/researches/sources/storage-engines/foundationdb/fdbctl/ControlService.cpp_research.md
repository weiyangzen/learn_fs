# sources/storage-engines/foundationdb/fdbctl/ControlService.cpp

## Purpose
This file provides the minimal implementation for `ControlServiceImpl` construction when Flow gRPC is enabled. The actual RPC method definitions live mostly in the header through a macro.

## Important APIs, Types, And Functions
The only implemented function is `ControlServiceImpl::ControlServiceImpl(Reference<IDatabase> db)`, which initializes the generated gRPC service base and stores the database reference in `db_`.

## Control Flow
Construction is direct and has no branching. RPC handling flow is defined in `ControlService.h`, where each gRPC method calls `handleRequestOnMainThread`.

## State And Persistence Behavior
The service stores an in-memory `Reference<IDatabase>`. It does not persist anything itself; command handlers mutate cluster state through the database reference.

## Dependencies And Integration Points
It depends on `ControlService.h`, `fmt`, `<chrono>`, and `FLOW_GRPC_ENABLED`. It integrates the generated gRPC service with FoundationDB’s database handle.

## Risks And Edge Cases
This source file is intentionally sparse, so constructor changes must be coordinated with header-defined RPC behavior. Unused includes may drift. No lifecycle/shutdown logic exists here.

## Test Signals
Construction tests should verify the service can be instantiated with a database reference in gRPC builds and that linked RPC methods resolve from the header-generated overrides.
