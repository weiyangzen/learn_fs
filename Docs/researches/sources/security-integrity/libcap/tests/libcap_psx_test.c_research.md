# sources/security-integrity/libcap/tests/libcap_psx_test.c

Purpose: C stress test that libcap operations linked with libpsx keep security state coherent across threads and forks.

Important APIs/functions: `thread_fork_exit()` forks from a thread, reads/writes keepcaps via `cap_prctl()` and `cap_prctlw()`, and verifies child state can change independently. Main starts ten threads while toggling keepcaps.

Control flow: each loop creates a worker thread, toggles keepcaps process-wide through libcap, verifies current process state, and allows workers to fork and validate their own transitions.

State and dependencies: uses pthreads, fork/wait, libcap prctl wrappers, libpsx linkage, and keepcaps state.

Risks and test signals: catches races between PSX fan-out, thread creation, and fork inheritance. Failure indicates process-wide security state is not consistently synchronized.
