# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir04.c

Purpose: Verify that user cannot create a directory inside directory owned by another user with restrictive permissions and that the errno is set to EACCESS.

Important APIs/types/functions: mkdir, tst_test, tst_uid, tst_res, tst_get_uids, SAFE_MKDIR, SAFE_CHOWN, SAFE_SETREUID; local functions detected: verify_mkdir, setup; key constants/macros: TESTDIR, TESTSUBDIR

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
