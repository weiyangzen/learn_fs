# sources/test-tools/ior/src/test/lib.c

Purpose: C API smoke test for calling `ior_run()` and `mdtest_run()` through the static library.

Important APIs: initializes MPI, gets rank, and on rank 0 calls `ior_run(3, {"./ior","-a","DUMMY"}, MPI_COMM_SELF, stdout)` and `mdtest_run(3, {"./mdtest","-a","DUMMY"}, MPI_COMM_SELF, stdout)`. It checks for NULL results and frees the IOR result's `platform` string and struct.

Control flow: only rank 0 runs the library calls; all ranks finalize MPI and return `ret`.

State and persistence: DUMMY backend should avoid real filesystem effects. The mdtest result is not freed, so the test leaks it until process exit.

Dependencies and integration: includes public IOR and mdtest headers, links against `libaiori.a`, and is listed in Automake tests as `testlib`.

Risks: only checks non-NULL return values. Does not validate rates, error counts, or cleanup. Running library calls on `MPI_COMM_SELF` avoids multi-rank behavior. The IOR result free is manual and partial, which may drift from real ownership expectations.

Test signals: confirms that the public C API can be linked and called with DUMMY backend under MPI initialization.
