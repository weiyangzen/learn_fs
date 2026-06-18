<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/059 -->
# sources/test-tools/xfstests/tests/ext4/059

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/059_research.md`.

Source read: 47 lines, SHA256 prefix `5c74bc2a23bc9193`.

Purpose: FS QA Test No. 059 A regression test for b55c3cd102a6 ("ext4: add reserved GDT blocks check"). Make sure there's not kernel crash, if resize an ext4 which resize_inode feature is disabled but has reserved GDT blocks..

Important APIs/types/functions: test tags `auto resize quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit b55c3cd102a6 \`, `_require_command "$RESIZE2FS_PROG" resize2fs`, `_require_command "$DEBUGFS_PROG" debugfs`, `_require_scratch_size_nocheck $((1024 * 1024))`; key variables `dev_size=$((512 * 1024 * 1024))`, `MKFS_OPTIONS="-O ^resize_inode $MKFS_OPTIONS" _scratch_mkfs_sized $dev_size \`, `MOUNT_OPTIONS="$MOUNT_OPTIONS -o noblock_validity"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: _require_command "$RESIZE2FS_PROG" resize2fs; L21: _require_command "$DEBUGFS_PROG" debugfs; L22: _require_scratch_size_nocheck $((1024 * 1024)); L26: MKFS_OPTIONS="-O ^resize_inode $MKFS_OPTIONS" _scratch_mkfs_sized $dev_size \; L30: $DEBUGFS_PROG -w -R "set_super_value s_reserved_gdt_blocks 100" $SCRATCH_DEV \; L32: $DEBUGFS_PROG -R "show_super_stats -h" $SCRATCH_DEV 2>/dev/null | \; L40: _scratch_mount; L43: $RESIZE2FS_PROG $SCRATCH_DEV 1G >> $seqres.full 2>&1.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; edits or inspects ext metadata directly; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/059 -->
