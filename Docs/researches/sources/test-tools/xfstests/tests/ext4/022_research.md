<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/022 -->
# sources/test-tools/xfstests/tests/ext4/022

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/022_research.md`.

Source read: 155 lines, SHA256 prefix `01fe9436de61bcef`.

Purpose: FS QA Test 022 Test extending of i_extra_isize code.

Important APIs/types/functions: test tags `auto quick attr dangerous`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_require_scratch`, `_require_dumpe2fs`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_attrs`, `_exclude_scratch_mount_option dax`; helper functions `do_setfattr()`, `create_xattr_file()`; key variables `BLOCK_SIZE=4096`, `INODE_SIZE=1024`, `XATTR_SPACE=256`, `GROW_EXTRA_ISIZE=80`, `GROW_MIN_EXTRA_ISIZE=16`, `ISIZE=$($DUMPE2FS_PROG -h $SCRATCH_DEV 2>/dev/null |`, `BLOCK_XATTR_SPACE=$(($BLOCK_SIZE - 36))`, `GOOD_OLD_ISIZE=128`, `WANT_ISIZE=$(($INODE_SIZE-$GOOD_OLD_ISIZE-$XATTR_SPACE))`, `NEW_ISIZE=$(($WANT_ISIZE+$GROW_EXTRA_ISIZE))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `do_setfattr()`, `create_xattr_file()`. Representative operation sequence: L25: _require_dumpe2fs; L26: _require_command "$DEBUGFS_PROG" debugfs; L32: _exclude_scratch_mount_option dax; L44: _scratch_mkfs >> $seqres.full 2>&1; L46: ISIZE=$($DUMPE2FS_PROG -h $SCRATCH_DEV 2>/dev/null |; L59: $DEBUGFS_PROG -w -R "ssv want_extra_isize $WANT_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L60: $DEBUGFS_PROG -w -R "ssv min_extra_isize $WANT_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L62: _scratch_mount; L125: _scratch_unmount; L129: $DEBUGFS_PROG -w -R "ssv want_extra_isize $NEW_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L130: $DEBUGFS_PROG -w -R "ssv min_extra_isize $NEW_MIN_ISIZE" $SCRATCH_DEV >> $seqres.full 2>&1; L132: _scratch_mount; L145: _scratch_unmount; L149: $DEBUGFS_PROG -R "stat $FILE" $SCRATCH_DEV 2>/dev/null | \.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/022 -->
