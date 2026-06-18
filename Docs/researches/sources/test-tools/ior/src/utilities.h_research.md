# sources/test-tools/ior/src/utilities.h

Purpose: shared utility declarations and global runtime variables for IOR benchmark components.

Important APIs and types: declares process globals (`rank`, `rankOffset`, `verbose`, `testComm`, `out_resultfile`, `outputFormat`), `MAX_PATHLEN`, `ERROR_LOCATION`, memory pattern APIs, CUDA initialization, filesystem reporting, regex, hint handling, human-readable formatting, MPI topology helpers, stonewall status helpers, timing helpers, `OpTimer`, random helpers, and aligned buffer allocation.

Control flow and integration: included by mdtest, md-workbench, parse_options, AIORI backends, and tests. Callers use the functions after MPI and output globals have been initialized by the benchmark entry point.

State and persistence: header exposes global mutable state, so any including module can read or alter benchmark-wide behavior. Several functions persist data through files, but paths are supplied by callers.

Risks: broad header coupling makes independent testing harder. `set_o_direct_flag(int *fd)` is declared as if it mutates a file descriptor, while implementation mutates an open flag bitmask. `PrintTimestamp()` is marked TODO for removal. Ownership and thread-safety for returned static strings are not documented.

Test signals: compile all users with this header, validate CPU and CUDA conditional declarations, and run API-level tests for exported helpers.
