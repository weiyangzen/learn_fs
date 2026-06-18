<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/311 -->
# sources/test-tools/xfstests/tests/btrfs/311

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/311_research.md`.

Source read: 85 lines, SHA256 prefix `895ad85707e3147b`.

Purpose: FS QA Test 311 Mount the device twice check if the reflink works, this helps to ensure device is mounted as the same device. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick subvol tempfsid`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`, `. ./common/reflink`; requirements/fixed gates `_require_cp_reflink`, `_require_scratch`, `_require_btrfs_fs_feature temp_fsid`; helper functions `_cleanup()`, `same_dev_mount()`, `same_dev_subvol_mount()`; key variables `mnt1=$TEST_DIR/$seq/mnt1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `same_dev_mount()`, `same_dev_subvol_mount()`. Representative operation sequence: L27: _require_btrfs_fs_feature temp_fsid; L32: same_dev_mount(); L36: _scratch_mkfs >> $seqres.full 2>&1; L38: _scratch_mount; L39: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/foo | \; L43: _mount $SCRATCH_DEV $mnt1; L47: md5sum $SCRATCH_MNT/foo | _filter_scratch; L48: md5sum $mnt1/bar | _filter_test_dir; L50: _check_temp_fsid $SCRATCH_DEV; L53: same_dev_subvol_mount(); L56: _scratch_mkfs >> $seqres.full 2>&1; L58: _scratch_mount; L59: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol | _filter_scratch; L61: $XFS_IO_PROG -fc 'pwrite -S 0x61 0 9000' $SCRATCH_MNT/subvol/foo | \; L65: _mount -o subvol=subvol $SCRATCH_DEV $mnt1; L69: md5sum $SCRATCH_MNT/subvol/foo | _filter_scratch; L70: md5sum $mnt1/bar | _filter_test_dir; L72: _check_temp_fsid $SCRATCH_DEV.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include Mount the device again to a different mount point; Checksum of reflinked files; Mounting a subvol; Checksum of reflinked files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/311 -->
