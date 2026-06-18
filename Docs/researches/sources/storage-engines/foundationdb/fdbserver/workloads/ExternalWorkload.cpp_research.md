# sources/storage-engines/foundationdb/fdbserver/workloads/ExternalWorkload.cpp

Purpose: Provides the `External` workload adapter that dynamically loads a shared library and runs a C++ or C workload implementation through FoundationDB's workload plugin interfaces.

Important APIs/types/functions: `ExternalWorkload`, `FDBWorkloadContext`, `FDBWorkload`, `FDBLoggerImpl`, `FDBPromiseImpl`, C API translators for metrics, promises, and context, `loadLibrary`, `loadFunction`, `ThreadSafeDatabase`, `ThreadSafeTransaction`, `workloadFactory`, and `workloadCFactory`.

Control flow: The constructor resolves `libraryPath/lib<name>`, loads it, then either obtains a C `workloadCFactory` or C++ `workloadFactory`, creates the named workload, and calls `init`. `setup`, `start`, and `check` wrap the tester `Database` as a `ThreadSafeDatabase`, pass a generic promise into the external workload, and await the result. Metrics are converted from `FDBPerfMetric` to tester `PerfMetric`.

State and persistence behavior: Persistent state is owned by the external workload. This adapter owns the dynamic library handle, external workload instance, and success flag. It closes the library in the destructor. C promise/context wrappers allocate memory that external code must free through provided vtables.

Dependencies/integration: It bridges Flow main-thread scheduling, thread futures, platform dynamic loading, trace logging, workload API versioning, and simulator process identity.

Risks: ABI/API mismatches, missing symbols, and external workload bugs become runtime failures. `keepAlive` futures are called but not retained, so database lifetime depends on external promise completion behavior. The factory variable is named `CycleWorkloadFactory` despite registering `ExternalWorkload`, which is confusing but local symbol naming only.

Test signals: `ExternalWorkloadLoad`, `ExternalWorkloadLoadError`, `ExternalCFactoryNotFound`, `ExternalFactoryNotFound`, `WorkloadNotFound`, `ExternalWorkloadFailure`, external trace events, and external metric output.
