<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/315 -->
# sources/test-tools/xfstests/tests/btrfs/315

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/315_research.md`.

Source read: 76 lines, SHA256 prefix `23311af82c16a616`.

Purpose: FS QA Test 315 Verify if the seed and device add to a tempfsid filesystem fails and balance devices is successful..

Important APIs/types/functions: test tags `auto quick volume seed balance tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch_dev_pool 3`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `seed_device_must_fail()`, `device_add_must_fail()`; key variables `tempfsid_mnt=$TEST_DIR/$seq/tempfsid_mnt`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `seed_device_must_fail()`, `device_add_must_fail()`. Representative operation sequence: L23: _require_scratch_dev_pool 3; L24: _require_btrfs_fs_feature temp_fsid; L26: _scratch_dev_pool_get 3; L35: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L37: $BTRFS_TUNE_PROG -S 1 ${SCRATCH_DEV}; L38: $BTRFS_TUNE_PROG -S 1 ${SCRATCH_DEV_NAME[1]}; L40: _scratch_mount 2>&1 | _filter_scratch; L41: _mount ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt} 2>&1 | _filter_error_mount; L48: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L49: _scratch_mount; L50: _mount ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt}; L52: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | \; L55: $BTRFS_UTIL_PROG device add -f ${SCRATCH_DEV_NAME[2]} ${tempfsid_mnt} 2>&1 | \; L56: grep -v "Performing full device TRIM" | _filter_scratch_pool; L59: _run_btrfs_balance_start ${tempfsid_mnt}; L66: _scratch_unmount; L72: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include Balance must be successful.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/315 -->
