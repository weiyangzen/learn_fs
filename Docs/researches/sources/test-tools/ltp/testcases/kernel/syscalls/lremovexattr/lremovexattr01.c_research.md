# sources/test-tools/ltp/testcases/kernel/syscalls/lremovexattr/lremovexattr01.c

Purpose: lremovexattr(2) removes the extended attribute identified by a name and associated with a given path in the filesystem. Unlike removexattr(2), lremovexattr(2) removes the attribute from the symbolic link only, and not the file. This test verifies that a simple call to lremovexattr(2) removes, indeed, a previously set attribute key/value from a symbolic link, and the symbolic link _only_. Note: According to attr(5), extended attributes are interpreted differently from regular files, directories and symbolic links. User attributes are only allowed for regular files and directories, thus the need of using trusted. attributes for this test.

Important APIs/types/functions: lremovexattr, lsetxattr, setxattr, getxattr, removexattr, symlink, memset, tst_test, SAFE_SETXATTR, SAFE_LSETXATTR, TST_RET, tst_res, TST_ERR, tst_brk, SAFE_REMOVEXATTR, SAFE_TOUCH, TST_TEST_TCONF; local functions detected: verify_lremovexattr, setup; key constants/macros: ENOATTR, XATTR_KEY, XATTR_VALUE, XATTR_VALUE_SIZE, MNTPOINT, FILENAME, SYMLINK

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_lremovexattr, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: set attribute on both: file and symlink remove attribute from symlink only
