# sources/test-tools/xfstests/tests/nfs/001


Purpose: NFSv4 ACL regression test for `nfs4_getfacl` near page-sized ACL buffers, guarding against ERANGE from getxattr.


Important APIs, helpers, and commands: Uses `_require_test_nfs_version 4`, `_require_command` for `nfs4_setfacl`/`nfs4_getfacl`, and builds an ACL list with about 200 numeric ACEs.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_command`, `_require_test_nfs_version`.



Control flow, state, dependencies, risks, and test signals: It creates a file/list pair in `$TEST_DIR`, writes OWNER, many numeric, GROUP, and EVERYONE ACEs to make the ACL close to a 4KiB page, applies it with nfs4_setfacl, dumps it to full output, and counts lines beginning with `A`. State is the file’s NFSv4 ACL on the mounted NFS test export. Dependencies are NFSv4 mount and nfs4-acl tools. Risks are non-4K page assumptions and server ACL limits. Signal is the expected ACE count rather than ERANGE. Source size is 50 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
