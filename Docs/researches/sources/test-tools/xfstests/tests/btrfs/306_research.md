<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/306 -->
# sources/test-tools/xfstests/tests/btrfs/306

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/306_research.md`.

Source read: 59 lines, SHA256 prefix `582ac8f7990d34e0`.

Purpose: FS QA Test 306 Test on-disk layout of RAID Stripe Tree Metadata by writing 4k to an emppty file at offset 64k with one stripe pre-filled on an otherwise pristine filesystem..

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`, `_require_btrfs_support_sectorsize 4096`; helper functions `test_4k_write_64koff()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_4k_write_64koff()`. Representative operation sequence: L17: _require_btrfs_command inspect-internal dump-tree; L18: _require_btrfs_mkfs_feature "raid-stripe-tree"; L19: _require_scratch_dev_pool 4; L20: _require_btrfs_fs_feature "raid_stripe_tree"; L21: _require_btrfs_fs_feature "free_space_tree"; L22: _require_btrfs_free_space_tree; L23: _require_btrfs_no_compress; L24: _require_btrfs_support_sectorsize 4096; L31: _scratch_dev_pool_get $ndevs; L34: _scratch_pool_mkfs -s 4k -d $profile -m $profile -O raid-stripe-tree; L35: _scratch_mount; L38: $XFS_IO_PROG -fc "pwrite 0 64k" "$SCRATCH_MNT/bar" | _filter_xfs_io; L40: $XFS_IO_PROG -fc "pwrite 64k 4k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L42: _scratch_cycle_mount; L43: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L45: _scratch_unmount; L47: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L50: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 4k write to an empty file at offset 64k with one stripe prefilled =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/306 -->
