## sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.h

Purpose: declares the C++ workload factory registry used by external workload shared libraries.

Important APIs and types: `IFDBWorkloadFactory` abstracts typed workload construction. `FDBWorkloadFactoryImpl` derives from `FDBWorkloadFactory`, owns static `factories()`, and implements name-based creation. Template `FDBWorkloadFactoryT<WorkloadType>` registers a workload type by name and creates `shared_ptr<WorkloadType>`. `extern "C" DLLEXPORT FDBWorkloadFactory* workloadFactory(FDBLogger*)` is the loader entry point.

Control flow: including this header in a workload file allows a static `FDBWorkloadFactoryT` instance to self-register with the map at load time.

State and persistence: defines process-global registration state, not database persistence.

Dependencies and integration points: includes `foundationdb/CppWorkload.h`; used by `SimpleWorkload.cpp` and implemented in `workloads.cpp`.

Risks: global static registration can fail silently if object files are not linked into the shared library. The registry uses raw pointers to static factory objects.

Test signals: exported `workloadFactory` plus registered names are required for any C++ workload test to run.
