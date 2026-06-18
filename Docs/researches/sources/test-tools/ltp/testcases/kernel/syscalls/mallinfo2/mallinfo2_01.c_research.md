# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo2/mallinfo2_01.c

Purpose: Basic mallinfo2() test. Test hblkhd member of struct mallinfo2 whether overflow when setting 2G size. Deprecated mallinfo() overflow in this case, that was the point for creating mallinfo2().

Important APIs/types/functions: mallinfo, mallinfo2, tst_safe_macros, tst_brk, tst_res, tst_test, TST_TEST_TCONF; local functions detected: test_mallinfo2; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: test_mallinfo2.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
