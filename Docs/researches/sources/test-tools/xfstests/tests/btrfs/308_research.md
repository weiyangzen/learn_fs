<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/308 -->
# sources/test-tools/xfstests/tests/btrfs/308

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/308_research.md`.

Source read: 61 lines, SHA256 prefix `47905cfb3600e301`.

Purpose: FS QA Test 308 Test on-disk layout of RAID Stripe Tree Metadata by writing 128k to an empty file on a filesystem that has one stripe already pre-filled. Afterwards overwrite a portion of the file..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_no_nodatacow`; helper functions `test_128k_write_overwrite()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_128k_write_overwrite()`. Representative operation sequence: L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_btrfs_mkfs_feature "raid-stripe-tree"; L19: _require_scratch_dev_pool 4; L20: _require_btrfs_fs_feature "raid_stripe_tree"; L21: _require_btrfs_fs_feature "free_space_tree"; L22: _require_btrfs_free_space_tree; L23: _require_btrfs_no_compress; L24: _require_btrfs_no_nodatacow; L33: _scratch_dev_pool_get $ndevs; L36: _scratch_pool_mkfs -d $profile -m $profile -O raid-stripe-tree; L37: _scratch_mount; L39: $XFS_IO_PROG -fc "pwrite -W 0 32k" "$SCRATCH_MNT/bar" | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite -W 0 128k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L41: $XFS_IO_PROG -fc "pwrite -W 64k 8k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L43: _scratch_cycle_mount; L44: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L46: _scratch_unmount; L48: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 128k write to empty file with 1st stripe partially prefilled then overwrite =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/308 -->
