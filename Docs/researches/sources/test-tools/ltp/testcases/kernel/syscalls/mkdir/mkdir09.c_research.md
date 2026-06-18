# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir09.c

Purpose: Create multiple processes which create subdirectories in the same directory multiple times within test time.

Important APIs/types/functions: mkdir, tst_test, tst_safe_pthread, TST_EXP_FAIL_SILENT, TST_PASS, tst_res, TST_EXP_PASS_SILENT, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN, SAFE_MKDIR; local functions detected: test1, test2, test3, verify_mkdir, setup; key constants/macros: MNTPOINT, MODE_RWX, DIR_NAME, DIR_NAME_GROUP, NCHILD

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test1, test2, test3, verify_mkdir, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases; process/thread timing is part of the signal and can make failures noisy.

Test signals: TST_EXP_PASS success assertions; TST_EXP_FAIL errno assertions; explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Routine which attempts to create directories in the test directory that already exist. Child routine which attempts to remove directories from the test directory which do not exist.
