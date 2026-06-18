# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/listxattr04.c

Purpose: Test reproducer for a bug introduced in 8b0ba61df5a1 ("fs/xattr.c: fix simple_xattr_list to always include security.* xattrs") and fixed in 800d0b9b6a8b (fs/xattr.c: fix simple_xattr_list()). Bug can be reproduced when SELinux and ACL are activated on inodes as following: $ touch testfile $ setfacl -m u:myuser:rwx testfile $ getfattr -dm. /tmp/testfile Segmentation fault (core dumped) The reason why this happens is that simple_xattr_list() always includes security.* xattrs without resetting error flag after security_inode_listsecurity(). This results into an incorrect length of the returned xattr name if POSIX ACL is also applied on the in...

Important APIs/types/functions: listxattr, acl_from_text, acl_set_file, memset, tst_test, tst_brk, tst_res, tst_lsm_enabled, SAFE_TOUCH, tst_tag, TST_TEST_TCONF; local functions detected: verify_xattr, run, setup, cleanup; key constants/macros: ACL_PERM, TEST_FILE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: verify_xattr, run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; filesystem extended attributes and ACL metadata. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; <sys/xattr.h> availability; libacl/POSIX ACL support; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; xattr namespace, ACL, or LSM policy differences may convert failures into TCONF/TBROK.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: HAVE_SYS_XATTR_H && HAVE_LIBACL
