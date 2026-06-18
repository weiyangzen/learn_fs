# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/workloads.h

Purpose: Defines the core workload abstraction, factories, option helpers, key-value workload base class, compound workload container, failure-injection support, and `quietDatabase` declaration.

Important APIs/types/functions: `WorkloadContext` carries options, client IDs, shared random number, DB info, connection record, and urgent-check ranges. `getOption` overloads, `poisson`, `uniform`, and `emplaceIndex` are shared helpers. `TestWorkload` defines `initialized`, `description`, `setup`, `start`, `check`, `getMetrics`, and phase bits. `TestWorkloadImpl` supplies descriptions from `Workload::NAME`. `FailureInjectionWorkload`, `IFailureInjectorFactory`, `FailureInjectorFactory`, `CompoundWorkload`, `ClientWorkload`, `KVWorkload`, `IWorkloadFactory`, `WorkloadFactory`, `REGISTER_WORKLOAD`, and `quietDatabase` form the registration/execution framework.

Control flow: Workload factories register statically by name. `IWorkloadFactory::create` looks up the requested `testName`. `WorkloadFactory` may wrap workloads in `ClientWorkload` for untrusted simulated clients. `TestWorkload` constructor consumes `runSetup` and initializes phase flags. Compound/failure-injection runtime flow is implemented in `WorkloadUtils.cpp`.

State and persistence behavior: `WorkloadContext` and workload objects hold per-client in-memory state. `KVWorkload` generates deterministic key/value content based on configured ranges. Actual database persistence is performed by concrete workload implementations, not this header.

Dependencies and integration points: Includes native API, database context clone support, simulation policy, tester interface, workload key definitions, and STL containers. Used by nearly every workload and by `TesterServer.cpp`.

Risks: Static registration order and duplicate workload names are guarded by asserts. Option consumption mutates `VectorRef<KeyValueRef>` values, so copies/ownership must be understood. `KVWorkload::randomValue` returns a `StringRef` over string memory passed into Flow's string wrapper; this relies on correct `StringRef`/`Value` ownership behavior in the constructor path.

Test signals: Workload creation failures emit `TestCreationError`; invalid options surface through option parsers. Concrete workload tests validate the framework indirectly.
