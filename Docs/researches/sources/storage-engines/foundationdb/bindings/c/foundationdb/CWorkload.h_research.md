# sources/storage-engines/foundationdb/bindings/c/foundationdb/CWorkload.h

## Purpose
`CWorkload.h` defines the pure-C external workload ABI for FoundationDB simulation/client testing. It mirrors the C++ workload API in `CppWorkload.h` using opaque pointers and virtual-table structs so workloads can be implemented in C.

## Important APIs, Types, And Functions
- `FDB_WORKLOAD_API_VERSION` identifies the ABI version.
- Opaque types include `OpaquePromise`, `OpaqueWorkload`, `OpaqueWorkloadContext`, and `OpaqueMetrics`.
- `FDBSeverity`, `FDBStringPair`, and `FDBMetric` model trace severity, detail key/values, and metric entries.
- `FDBString`, `FDBMetrics`, and `FDBPromise` wrap owned/borrowed C++ objects with function tables.
- `FDBWorkloadContext` exposes trace, process id, simulated time, random numbers, options, client identity, shared random seed, and delay future creation.
- `FDBWorkload` exposes workload lifecycle methods `setup`, `start`, `check`, `getMetrics`, and `getCheckTimeout`.
- `workloadCFactory(const char* name, FDBWorkloadContext context)` is the required entrypoint.

## Control Flow
The simulator loads a C workload shared library, calls `workloadCFactory()`, then drives setup/start/check stages sequentially. Each stage receives a promise and must resolve it asynchronously or free it. Workloads must not block; they should register callbacks around database futures and return.

## State And Persistence Behavior
The header defines ownership rules rather than state. Workload implementations own their `inner` workload pointer and must free it through the vtable. `FDBPromise` represents a pending simulation stage; leaking or not resolving it can hang the simulation. Database persistence occurs through `FDBDatabase` and C API functions invoked by implementations.

## Dependencies And Integration Points
It forward-declares C API `FDBFuture` and `FDBDatabase`, and is built/installed for external workloads. CMake builds a sample `c_workloads` shared library that includes this interface.

## Risks And Edge Cases
No function pointer in a returned workload may be null. Pointer arguments are mostly borrowed, so C workloads must not retain them beyond valid lifetimes unless documented. Blocking in callbacks or stages can stall simulation. ABI evolution must append to virtual tables to preserve compatibility.

## Test Signals
External workload libraries built in CMake provide compile/link coverage. Simulation/client workload tests validate lifecycle behavior when these interfaces are loaded.
