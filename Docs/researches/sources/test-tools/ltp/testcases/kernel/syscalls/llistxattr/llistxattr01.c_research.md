# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/llistxattr01.c

Purpose: Basic test for llistxattr(2), retrieves the list of extended attribute names associated with the link itself in the filesystem.

Important APIs/types/functions: llistxattr, lsetxattr, symlink, tst_test, TST_RET, tst_res, SAFE_TOUCH, SAFE_SYMLINK, SAFE_LSETXATTR, TST_TEST_TCONF; local functions detected: has_attribute, verify_llistxattr, setup; key constants/macros: SECURITY_KEY1, SECURITY_KEY2, VALUE, VALUE_SIZE, KEY_SIZE, TESTFILE, SYMLINK

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: has_attribute, verify_llistxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
