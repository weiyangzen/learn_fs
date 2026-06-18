<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/304 -->
# sources/test-tools/xfstests/tests/btrfs/304

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/304_research.md`.

Source read: 56 lines, SHA256 prefix `c5a89bcfff508cab`.

Purpose: FS QA Test 304 Test on-disk layout of RAID Stripe Tree Metadata writing 4k to a new file on a pristine file system..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_support_sectorsize 4096`; helper functions `test_4k_write()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_4k_write()`. Representative operation sequence: L16: _require_btrfs_command inspect-internal dump-tree; L17: _require_btrfs_mkfs_feature "raid-stripe-tree"; L18: _require_scratch_dev_pool 4; L19: _require_btrfs_fs_feature "raid_stripe_tree"; L20: _require_btrfs_fs_feature "free_space_tree"; L21: _require_btrfs_free_space_tree; L22: _require_btrfs_no_compress; L23: _require_btrfs_support_sectorsize 4096; L30: _scratch_dev_pool_get $ndevs; L33: _scratch_pool_mkfs -s 4k -d $profile -m $profile -O raid-stripe-tree; L34: _scratch_mount; L36: $XFS_IO_PROG -fc "pwrite 0 4k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L38: _scratch_cycle_mount; L39: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L41: _scratch_unmount; L43: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L46: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test basic 4k write =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/304 -->
