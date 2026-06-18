# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore02.c

Purpose: This test case provides a functional validation for mincore system call. We mmap a file of known size (multiple of page size) and lock it in memory. Then we obtain page location information via mincore and compare the result with the expected value.

Important APIs/types/functions: write, open, close, mmap, munmap, mlock, munlock, mincore, memset, tst_test, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_CLOSE, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_MMAP, SAFE_MLOCK, TST_EXP_PASS, TST_EXP_EQ_SZ; local functions detected: cleanup, setup, check_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, check_mincore.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
