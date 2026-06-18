# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_get_self_attr02.c

Purpose: Verify that lsm_get_self_attr syscall is acting correctly when ctx is NULL. The syscall can behave in different ways according to the current system status: - if any LSM is running inside the system, the syscall will pass and it will provide a size as big as the attribute - if no LSM(s) are running inside the system, the syscall will fail with -1 return code

Important APIs/types/functions: lsm_get_self_attr, TST_EXP_POSITIVE, TST_EXP_EXPR, TST_EXP_FAIL, SAFE_SYSCONF, tst_test; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
