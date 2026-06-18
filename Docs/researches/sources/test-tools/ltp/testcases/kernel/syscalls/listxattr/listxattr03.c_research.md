# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr03.c

Purpose: Test for returning the current size of the list of extended attribute names, with size specified as zero.

Important APIs/types/functions: listxattr, setxattr, tst_test, TST_RET, tst_res, SAFE_TOUCH, SAFE_SETXATTR, TST_TEST_TCONF; local functions detected: check_suitable_buf, verify_listxattr, setup; key constants/macros: SECURITY_KEY, VALUE, VALUE_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_suitable_buf, verify_listxattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
