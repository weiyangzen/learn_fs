# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir02.c

Purpose: Verify that new directory created by mkdir(2) inherites the group ID from the parent directory and S_ISGID bit, if the S_ISGID bit is set in the parent directory.

Important APIs/types/functions: mkdir, stat, tst_test, tst_uid, SAFE_MKDIR, SAFE_STAT, tst_res, SAFE_RMDIR, SAFE_GETPWNAM, tst_get_free_gid, SAFE_CHMOD, SAFE_CHOWN, SAFE_SETREGID, SAFE_SETREUID; local functions detected: verify_mkdir, setup; key constants/macros: TESTDIR1, TESTDIR2

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
