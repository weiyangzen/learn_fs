# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_set_self_attr01.c

Purpose: Verify that lsm_set_self_attr syscall is raising errors when invalid data is provided.

Important APIs/types/functions: lsm_get_self_attr, lsm_set_self_attr, memcpy, TST_EXP_EXPR, SAFE_SYSCONF, tst_brk, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_* value comparisons; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: just in case lsm_set_self_attr() pass , we won't change LSM configuration for the following process
