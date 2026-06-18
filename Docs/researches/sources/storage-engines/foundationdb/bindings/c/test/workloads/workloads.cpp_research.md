## sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.cpp

Purpose: implementation of the C++ workload factory registry exported to the simulation workload loader.

Important APIs and functions: `FDBWorkloadFactoryImpl::factories()` owns a static map from workload name to `IFDBWorkloadFactory*`; `create` looks up a name and returns a `shared_ptr<FDBWorkload>` or null; `workloadFactory(FDBLogger*)` exports a singleton `FDBWorkloadFactoryImpl`.

Control flow: workload implementations instantiate `FDBWorkloadFactoryT<T>` statics, which insert themselves into the static map before the loader calls `workloadFactory`. The loader then asks the returned factory to create named workloads.

State and persistence: only process-global registry state in the static map and factory singleton. No database state.

Dependencies and integration points: depends on `workloads.h` and `foundationdb/CppWorkload.h`; integrated by dynamic library loading and `DLLEXPORT` symbol lookup.

Risks: static initialization order matters between registration objects and factory lookup. Raw factory pointers are stored without ownership, assuming registration statics outlive all lookups.

Test signals: creation success for `SimpleWorkload` confirms registry wiring.
