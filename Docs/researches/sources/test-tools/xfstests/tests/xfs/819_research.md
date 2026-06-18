<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/819 -->
# sources/test-tools/xfstests/tests/xfs/819

Purpose: mkfs protofile regression test for creating filesystems with xattrs, special files, symlinks, setuid/setgid modes, and large file content.

Important APIs, types, and functions: constructs a protofile manually, writes source files with `xfs_io` and `devzero`, sets root/security/user/big xattrs with `attr`, formats with `_scratch_mkfs_xfs -p`, and validates using `lstat64`, `diff`, and attr listing.

Control flow: the test builds source files and a protofile tree, then `_verify_fs 2` unmounts, formats, checks, mounts, confirms xattr support, lists and filters metadata, compares file and symlink content, lists xattrs, and unmounts.

State and persistence behavior: temporary protofile and source files live under `$tmp` and `$TEST_DIR`; scratch filesystem is rebuilt from the protofile.

Dependencies and integration points: depends on attr tooling, mkfs protofile support, xfs scratch, lstat64/devzero helper programs, and no `rtinherit` mkfs option.

Risks and test signals: skips when protofile xattrs are unsupported. Signals are matching file tree metadata, valid bigfile content, and preserved xattrs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/819 -->
