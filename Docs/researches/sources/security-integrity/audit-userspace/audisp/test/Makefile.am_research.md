# sources/security-integrity/audit-userspace/audisp/test/Makefile.am

Purpose: Automake test definition for audisp unit/integration-style tests.

Important APIs, types, and functions: Sets `AM_CPPFLAGS` to include top-level, audisp, common, src, and lib headers; sets `AM_CFLAGS` with `_GNU_SOURCE`, warning flags, and optional ASAN flags; defines `check_PROGRAMS` and `TESTS` as `audisp-queue-test`, `audisp-llist-test`, and `pconfig-alloc-test`.

Control flow: During `make check`, Automake builds and runs all `check_PROGRAMS`. `audisp_queue_test` compiles `test-queue.c` and links `libqueue.la`, `libaucommon.la`, and pthreads. `audisp_llist_test` compiles `test-audispd-llist.c` and links `libdisp.la` plus common helpers. `pconfig_alloc_test` compiles the allocator-failure parser harness.

State and persistence: No runtime state in this file. It controls build/test graph state through Automake variables and optional ASAN instrumentation.

Dependencies and integration points: Integrates audisp tests with the top-level build. It depends on generated config headers and local libtool libraries from audisp/common.

Risks and edge cases: Tests rely on relative fixture paths such as `../../auparse/test/test3.log` at runtime. If build directories differ, `srcdir` handling must remain correct. ASAN flags apply uniformly to the test programs when `HAVE_ASAN` is set.

Test signals: This file is the authoritative list for the three audisp tests in this subset and provides the build signal that queue, plugin-list, and parser allocation-failure tests are expected to run under `make check`.
