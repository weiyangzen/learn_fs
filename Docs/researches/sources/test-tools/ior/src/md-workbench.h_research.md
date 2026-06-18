# sources/test-tools/ior/src/md-workbench.h

Purpose: public API and result contract for the md-workbench benchmark.

Important APIs and types: `time_statistics_t` stores per-operation latency quantiles and extrema. `mdworkbench_result_t` stores one phase result, including create/read/stat/delete latency stats, error count, throughput/rate, maximum operation time, runtime, and iterations completed. `mdworkbench_results_t` is a flexible-array container containing a count, total errors, and phase results. `md_workbench_run()` is the sole exported function and returns precreate, benchmark iteration, and cleanup results.

Control flow and integration: consumers call `md_workbench_run(argc, argv, MPI_Comm, FILE *)` after MPI is initialized. The implementation fills results in phase order as documented in the header comment: first precreate, then benchmark runs, then cleanup. It integrates with MPI, stdio logging, and the implementation in `md-workbench.c`.

State and persistence: the header does not own persistence, but its returned result pointer is heap allocated by the implementation. Callers must treat it as dynamically allocated memory and free it when done. The flexible array means callers should not stack-copy the structure without accounting for `count`.

Risks: the API does not expose an explicit destructor or allocation size. Callers must infer that `free()` is sufficient from the implementation. The comment says "iteration many benchmark runs", while adaptive waiting can return more benchmark result entries than the plain iteration count.

Test signals: compile-time users should include this header from C code, call the function under MPI, and verify `count`, phase ordering, and error aggregation against known small DUMMY/POSIX runs.
