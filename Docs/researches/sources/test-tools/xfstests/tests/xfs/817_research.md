<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/817 -->
# sources/test-tools/xfstests/tests/xfs/817

Purpose: functional test for repairing missing or corrupt XFS metadata-directory paths, especially `/rtgroups/0.rmap`, using raw online repair ioctls, `xfs_scrub`, and `xfs_repair`.

Important APIs, types, and functions: `prepare_fs` formats scratch, requires rmapbt/realtime/metadir/parent, records inode/generation pairs, and corrupts a parent pointer with xfs_db. `simple_online_repair` sequences directory, parent, metapath, and nlinks scrub/repair commands.

Control flow: the test runs three parts: direct xfs_io scrub/repair commands, full xfs_scrub, and offline xfs_repair. Each part prepares a fresh corrupted filesystem and validates with `_check_scratch_fs`.

State and persistence behavior: intentionally corrupts metadata parent pointers and directory links in the scratch filesystem, then verifies repair restoration before unmount.

Dependencies and integration points: depends on xfs_db link/unlink support, online repair, parent pointers, metadir, realtime, rmapbt, and scrub/repair tools.

Risks and test signals: destroying metadir paths can prevent mounts, so the online sequence is carefully ordered. Success is all three repair paths returning a consistent filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/817 -->
