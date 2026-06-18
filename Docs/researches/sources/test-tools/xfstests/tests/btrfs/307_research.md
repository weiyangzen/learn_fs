<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/307 -->
# sources/test-tools/xfstests/tests/btrfs/307

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/307_research.md`.

Source read: 57 lines, SHA256 prefix `14240aaac6c3ccdf`.

Purpose: FS QA Test 307 Test on-disk layout of RAID Stripe Tree Metadata by writing 128k to a new file on a pristine filesystem.

Important APIs/types/functions: test tags `auto quick raid remount volume raid-stripe-tree`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_btrfs_command inspect-internal dump-tree`, `_require_btrfs_mkfs_feature "raid-stripe-tree"`, `_require_scratch_dev_pool 4`, `_require_btrfs_fs_feature "raid_stripe_tree"`, `_require_btrfs_fs_feature "free_space_tree"`, `_require_btrfs_free_space_tree`, `_require_btrfs_no_compress`; helper functions `test_128k_write()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `test_128k_write()`. Representative operation sequence: L16: _require_btrfs_command inspect-internal dump-tree; L17: _require_btrfs_mkfs_feature "raid-stripe-tree"; L18: _require_scratch_dev_pool 4; L19: _require_btrfs_fs_feature "raid_stripe_tree"; L20: _require_btrfs_fs_feature "free_space_tree"; L21: _require_btrfs_free_space_tree; L22: _require_btrfs_no_compress; L31: _scratch_dev_pool_get $ndevs; L34: _scratch_pool_mkfs -d $profile -m $profile -O raid-stripe-tree; L35: _scratch_mount; L37: $XFS_IO_PROG -fc "pwrite 0 128k" "$SCRATCH_MNT/foo" | _filter_xfs_io; L39: _scratch_cycle_mount; L40: md5sum "$SCRATCH_MNT/foo" | _filter_scratch; L42: _scratch_unmount; L44: $BTRFS_UTIL_PROG inspect-internal dump-tree -t raid_stripe $SCRATCH_DEV_POOL |\; L47: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; btrfs on-disk tree inspection; visible subtest labels include = Test 128k write to empty file =.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/307 -->
