<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/314 -->
# sources/test-tools/xfstests/tests/btrfs/314

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/314_research.md`.

Source read: 76 lines, SHA256 prefix `aa76f986351a3531`.

Purpose: FS QA Test 314 Send and receive functionality test between a normal and tempfsid filesystem..

Important APIs/types/functions: test tags `auto quick snapshot send tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_require_scratch_dev_pool 2`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `send_receive_tempfsid()`; key variables `tempfsid_mnt=$TEST_DIR/$seq/tempfsid_mnt`, `sendfile=$TEST_DIR/$seq/replicate.send`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `send_receive_tempfsid()`. Representative operation sequence: L24: _require_scratch_dev_pool 2; L25: _require_btrfs_fs_feature temp_fsid; L27: _scratch_dev_pool_get 2; L39: _btrfs_mkfs_clone ${SCRATCH_DEV} ${SCRATCH_DEV_NAME[1]}; L40: _scratch_mount; L41: _mount $(_common_dev_mount_options) ${SCRATCH_DEV_NAME[1]} ${tempfsid_mnt}; L43: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' ${src}/foo | _filter_xfs_io; L44: _btrfs subvolume snapshot -r ${src} ${src}/snap1; L47: $BTRFS_UTIL_PROG send -f ${sendfile} ${src}/snap1 2>&1 | \; L50: $BTRFS_UTIL_PROG receive -f ${sendfile} ${dst} | \; L53: md5sum ${src}/foo | _filter_testdir_and_scratch; L55: md5sum ${dst}/snap1/foo | _filter_testdir_and_scratch; L64: _scratch_unmount; L72: _scratch_dev_pool_put.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/314 -->
