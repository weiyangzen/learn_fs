# sources/test-tools/ltp/testcases/kernel/syscalls/membarrier/membarrier01.c

Purpose: Basic tests for membarrier(2) syscall. Tests below are responsible for testing the membarrier(2) interface only, without checking if the barrier was successful or not. Check test_case structure for each test description.

Important APIs/types/functions: fork, waitpid, membarrier, tst_test, tst_res, tst_syscall, tst_brk, TST_RET, TST_ERR, SAFE_FORK, SAFE_WAITPID, tst_kvercmp; local functions detected: sys_membarrier, verify_membarrier, wrap_verify_membarrier, setup; key constants/macros: passed_ok, passed_unexpec, failed_ok, failed_ok_unsupported, failed_not_ok, failed_unexpec, skipped, skipped_fail

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: sys_membarrier, verify_membarrier, wrap_verify_membarrier, setup.

State and persistence behavior: child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; membarrier syscall command support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: membarrier cmd needs register cmd flags for given membarrier cmd
