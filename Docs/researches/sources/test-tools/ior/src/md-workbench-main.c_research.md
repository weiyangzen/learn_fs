# sources/test-tools/ior/src/md-workbench-main.c

## Purpose
Provides the standalone executable entry point for the metadata workbench tool.

## Important APIs, Types, And Functions
Includes MPI and `md-workbench.h`. Defines `main(int argc, char **argv)`, calls `MPI_Init`, invokes `md_workbench_run(argc, argv, MPI_COMM_WORLD, stdout)`, finalizes MPI, and returns 0.

## Control Flow
The wrapper initializes MPI before handing control to the metadata workbench implementation and finalizes MPI afterward. Commented lines show earlier API-check/debug use of returned phase statistics.

## State And Persistence Behavior
No local state is persisted. Runtime output goes to stdout through `md_workbench_run`; any filesystem effects are owned by the workbench implementation.

## Dependencies And Integration Points
Integrates the md-workbench library code with MPI process startup. It is separate from IOR's `ior_main` path but shares the same test-tools source tree and AIORI backends through md-workbench internals.

## Risks And Edge Cases
The return value from `md_workbench_run` is ignored, so failures may not affect process exit status unless that function aborts. MPI is always initialized/finalized here, making embedding or nested MPI ownership unsuitable.

## Test Signals
Executable smoke tests, option parsing through `md_workbench_run`, and failure-path tests that verify exit status behavior are the relevant signals.
