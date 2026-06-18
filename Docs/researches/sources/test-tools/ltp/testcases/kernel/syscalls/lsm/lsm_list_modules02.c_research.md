# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_list_modules02.c

Purpose: Verify that lsm_list_modules syscall is correctly recognizing LSM(s) enabled inside the system. [Algorithm] - read enabled LSM(s) inside /sys/kernel/security/lsm file - collect LSM IDs using lsm_list_modules syscall - compare the results, verifying that LSM(s) IDs are correct

Important APIs/types/functions: read, open, close, lsm_list_modules, memset, TST_EXP_POSITIVE, TST_EXP_EQ_LI, tst_brk, tst_res, SAFE_SYSCONF, SAFE_OPEN, SAFE_READ, SAFE_CLOSE, tst_test, tst_buffers; local functions detected: run, setup; key constants/macros: MAX_LSM_NUM

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; sysfs/securityfs/cgroup files used as capability or state sources. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_* value comparisons; explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
