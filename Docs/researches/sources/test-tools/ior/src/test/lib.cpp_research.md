# sources/test-tools/ior/src/test/lib.cpp

Purpose: C++ linkage smoke test for the C IOR and mdtest APIs.

Important APIs: wraps `ior.h` and `mdtest.h` in `extern "C"`, initializes MPI, and on rank 0 calls `ior_run()` and `mdtest_run()` with DUMMY backend parameters.

Control flow: mirrors `lib.c`, including rank-0-only API calls and MPI finalize.

State and persistence: no intended filesystem state because the DUMMY backend is used. The mdtest result allocation is not freed.

Dependencies and integration: requires a C++ compiler, MPI C++ compile path, and C ABI-compatible headers. The source is present but not listed in `Makefile.am`, so it may be a manual smoke test rather than an automated one.

Risks: C headers must remain valid under `extern "C"`. Because the file is not part of the declared Automake tests, C++ compatibility can regress unnoticed.

Test signals: manually compile with an MPI C++ compiler and link against the AIORI library; ideally add it to automated check targets if C++ API compatibility matters.
