## sources/storage-engines/foundationdb/bindings/c/test/workloads/SimpleWorkload.cpp

Purpose: C++ workload implementation for C API simulation testing. It populates many keys through asynchronous actor-like state machines, then runs concurrent read/commit clients and reports throughput/retry metrics.

Important APIs and types: `SimpleWorkload` derives from `FDBWorkload`. Nested `ActorBase` converts C futures into callback-driven actor states with one outstanding wait. `PopulateActor` batches inserts and commits with retry handling. `ClientActor` randomly reads keys, commits after `opsPerTx`, tracks gets/commits/retries, and retries on errors. `FDBWorkloadFactoryT<SimpleWorkload>` registers it by name.

Control flow: `init` reads options (`numTuples`, `numActors`, `insertsPerTx`, `opsPerTx`, `runFor`), seeds RNG, and selects API version. `setup` skips population for client 0 and otherwise partitions insert ranges across populate actors. `start` launches client actors, aggregates per-actor rates on completion, and resolves the promise. `check` returns success.

State and persistence: writes keys under `csimple/` with numeric string values. Transaction objects are reused/reset across retries and commits. Metrics vectors persist per workload instance until `getMetrics`.

Dependencies and integration points: uses the C API directly, `foundationdb/CppWorkload.h` through `workloads.h`, and the workload factory registry.

Risks: callback state assumes at most one outstanding wait per actor and terminates otherwise. `accumulateMetric` divides by vector size, so no completed actors would be unsafe. Error callbacks capture `error` inconsistently in two lambdas, making diagnostic output fragile.

Test signals: provides load-oriented validation for async callbacks, retry loops, commits, random reads, metrics, and workload factory registration.
