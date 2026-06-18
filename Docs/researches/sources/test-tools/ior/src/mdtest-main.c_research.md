# sources/test-tools/ior/src/mdtest-main.c

Purpose: minimal standalone executable entry point for mdtest.

Important APIs and functions: `main()` initializes MPI, calls `mdtest_run(argc, argv, MPI_COMM_WORLD, stdout)`, finalizes MPI, and returns zero.

Control flow: all option parsing, backend setup, benchmark phases, reporting, and result allocation are delegated to `mdtest_run()` in `mdtest.c`. The wrapper does not inspect the returned `mdtest_results_t *`.

State and persistence: no local persistent state. Runtime state and outputs are controlled by mdtest options and global state in `utilities.c`/`mdtest.c`. The returned result pointer is not freed here, so process exit is relied on for cleanup.

Dependencies and integration: includes `mdtest.h` and `aiori.h`; links against MPI and the IOR/AIORI library. It is the CLI bridge from the benchmark library API to a normal executable.

Risks: ignores a NULL result or benchmark error status and always returns success unless MPI itself aborts. It also leaks the returned result allocation for the lifetime of the process, which is harmless for a short-lived CLI but not a model for embedding.

Test signals: smoke test by running the mdtest binary with `-a DUMMY` and small item counts under `mpirun`; verify MPI init/finalize sequence and stdout reporting.
