<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/335 -->
# sources/test-tools/xfstests/tests/btrfs/335

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/335_research.md`.

Source read: 62 lines, SHA256 prefix `8905db2d6754428a`.

Purpose: FS QA Test 335 Regression test for a kernel crash when converting a zoned BTRFS from metadata DUP to RAID1 and one of the devices has a non 0 write pointer position in the target zone..

Important APIs/types/functions: test tags `auto zone quick volume raid`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_fixed_by_kernel_commit b0c26f479926 \`, `_require_scratch_dev_pool 2`, `_require_zoned_device ${devs[0]}`, `_require_zoned_device ${devs[1]}`, `_require_command "$BLKZONE_PROG" blkzone`; key variables `zones=$($BLKZONE_PROG report ${devs[1]} | $AWK_PROG '/em/ { print $2 }' |\`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L19: _require_scratch_dev_pool 2; L25: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L26: _scratch_mount; L29: $XFS_IO_PROG -fc "pwrite 0 128M" $SCRATCH_MNT/test | _filter_xfs_io; L32: $BTRFS_UTIL_PROG device add ${devs[1]} $SCRATCH_MNT >> $seqres.full; L43: $XFS_IO_PROG -fdc "pwrite $(($zone << 9)) 4096" ${devs[1]} > /dev/null 2>&1; L47: $BTRFS_UTIL_PROG balance start -mconvert=raid1 $SCRATCH_MNT 2>&1 |\; L50: _scratch_unmount; L54: $BTRFS_UTIL_PROG device remove --force missing $SCRATCH_MNT >> $seqres.full; L55: $BTRFS_UTIL_PROG balance start --full-balance $SCRATCH_MNT >> $seqres.full; L58: $BTRFS_UTIL_PROG filesystem df $SCRATCH_MNT |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/335 -->
