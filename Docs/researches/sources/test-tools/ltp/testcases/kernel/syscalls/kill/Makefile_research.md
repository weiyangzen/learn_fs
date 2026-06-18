# sources/test-tools/ltp/testcases/kernel/syscalls/kill/Makefile

Purpose: builds the kill syscall test directory. It declares `LTPLIBS = newipc`, includes common LTP testcase rules, links `kill05` with `-lltpnewipc` for its shared-memory synchronization helper use, and delegates to the generic leaf target. The Makefile has no runtime state; it records build dependencies for both legacy `test.h` tests and newer `tst_test.h` tests. Integration risk is missing the newipc library for `kill05`. Test signal is successful build of all kill test binaries.
