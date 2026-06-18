# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo02.c

Purpose: Basic mallinfo() test for malloc() using sbrk or mmap. It size > MMAP_THRESHOLD, it will use mmap. Otherwise, use sbrk.

Important APIs/types/functions: mallinfo, mallopt, tst_safe_macros, SAFE_MALLOC, tst_res, tst_test, TST_TEST_TCONF; local functions detected: test_mallinfo, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test_mallinfo, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
