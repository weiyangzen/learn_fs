# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore03.c

Purpose: mincore03 Testcase 1: Test shows that pages mapped as anonymous and not faulted, are reported as not resident in memory by mincore(). Testcase 2: Test shows that pages mapped as anonymous and faulted, are reported as resident in memory by mincore().

Important APIs/types/functions: mmap, munmap, mlock, munlock, mincore, tst_test, SAFE_MUNMAP, SAFE_MMAP, SAFE_MLOCK, tst_brk, tst_res, SAFE_MUNLOCK; local functions detected: cleanup, setup, test_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, test_mincore.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
