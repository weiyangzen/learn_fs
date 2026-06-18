<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/313 -->
# sources/test-tools/xfstests/tests/btrfs/313

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/313_research.md`.

Source read: 51 lines, SHA256 prefix `5655a85fa60227bc`.

Purpose: FS QA Test 313 Functional test for the tempfsid, clone devices created using the mkfs option..

Important APIs/types/functions: test tags `auto quick clone tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`, `. ./common/reflink`; requirements/fixed gates `_require_cp_reflink`, `_require_scratch_dev_pool 2`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`; key variables `mnt1=$TEST_DIR/$seq/mnt1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L24: _require_scratch_dev_pool 2; L25: _require_btrfs_fs_feature temp_fsid; L27: _scratch_dev_pool_get 2; L33: _btrfs_mkfs_clone ${SCRATCH_DEV_NAME[0]} ${SCRATCH_DEV_NAME[1]}; L36: _mount ${SCRATCH_DEV_NAME[0]} $SCRATCH_MNT; L37: _check_temp_fsid ${SCRATCH_DEV_NAME[0]}; L40: _mount ${SCRATCH_DEV_NAME[1]} $mnt1; L41: _check_temp_fsid ${SCRATCH_DEV_NAME[1]}; L43: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | _filter_xfs_io; L47: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: visible subtest labels include ---- clone_uuids_verify_tempfsid ----; Mounting original device; Mounting cloned device; cp reflink must fail.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/313 -->
