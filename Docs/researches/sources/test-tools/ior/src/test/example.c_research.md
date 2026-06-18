# sources/test-tools/ior/src/test/example.c

Purpose: minimal C smoke test for initializing an `IOR_param_t` and linking against IOR internals.

Important APIs: calls `MPI_Init()`, `init_IOR_Param_t(&test, MPI_COMM_WORLD)`, mutates a few fields (`blockSize`, `transferSize`, `segmentCount`, `numTasks`, `filePerProc`), prints `OK`, and finalizes MPI.

Control flow: no benchmark is run. The test only verifies that headers, MPI setup, and parameter initialization can compile and execute.

State and persistence: creates a stack `IOR_param_t`; no files or persistent benchmark data are created.

Dependencies and integration: includes `ior.h` and `ior-internal.h`, so it reaches into internal initialization APIs. It is built by `src/test/Makefile.am` as `testexample`.

Risks: assertions are included but unused. The test does not validate any initialized defaults or run AIORI operations, so it can pass despite behavioral regressions in the benchmark path.

Test signals: useful as a build/link smoke test. Stronger tests would assert initialized fields and run a tiny DUMMY backend operation.
