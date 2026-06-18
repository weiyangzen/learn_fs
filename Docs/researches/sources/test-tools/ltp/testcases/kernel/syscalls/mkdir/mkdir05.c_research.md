# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir05.c

Purpose: DESCRIPTION This test will verify the mkdir(2) creates a new directory successfully and it is owned by the effective UID and GID of the process.

Important APIs/types/functions: mkdir, stat, setuid, tst_test, TST_RET, tst_res, SAFE_STAT, SAFE_RMDIR, SAFE_GETPWNAM, SAFE_SETUID; local functions detected: verify_mkdir, setup; key constants/macros: PERMS, TESTDIR

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
