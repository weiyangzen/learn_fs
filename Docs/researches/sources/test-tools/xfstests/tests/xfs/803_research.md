<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/803 -->
# sources/test-tools/xfstests/tests/xfs/803

Purpose: functional coverage for low-level XFS filesystem property manipulation through `xfs_io` online commands and `xfs_db` offline attribute commands.

Important APIs, types, and functions: exercises `getfsprops`, `setfsprops`, `removefsprops`, `listfsprops`, `attr_get -Z`, `attr_set -Z`, `attr_remove -Z`, and `attr_list -Z`. It uses `filter_inum` to hide variable inode numbers.

Control flow: the online phase performs empty get/remove/list, set/list/get, child file and directory rejection, removal, long-name/value failures, and permission checks as `fsgqa`. The offline phase unmounts and repeats comparable xfs_db operations on root.

State and persistence behavior: the test writes and removes the fake root filesystem property `fakeproperty`, creates temporary child entries, and cleans the property with `attr -R -r`.

Dependencies and integration points: depends on test filesystem, xattrs, `xfs_io` fsprops support, `xfs_db attr_list`, and the xfstests attr helper.

Risks and test signals: coverage is sensitive to root-only semantics and maximum name/value sizes. Output verifies correct rejection, visibility through xattrs, and no leftover property state.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/803 -->
