# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr02.c

Purpose: Verify llistxattr(2) returns -1 and set proper errno: - ERANGE if the size of the list buffer is too small to hold the result - ENOENT if path is an empty string - EFAULT when attempted to read from a invalid address - ENAMETOOLONG if path is longer than allowed

Important APIs/types/functions: llistxattr, lsetxattr, symlink, memset, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_TOUCH, SAFE_SYMLINK, SAFE_LSETXATTR, TST_TEST_TCONF; local functions detected: verify_llistxattr, setup; key constants/macros: SECURITY_KEY, VALUE, VALUE_SIZE, TESTFILE, SYMLINK

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_llistxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
