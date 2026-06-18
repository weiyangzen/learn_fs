<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/312 -->
# sources/test-tools/xfstests/tests/btrfs/312

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/312_research.md`.

Source read: 115 lines, SHA256 prefix `7c644e14f2baa7c4`.

Purpose: FS QA Test 312 Test a scenario of a compressed send stream that triggered a bug in the extent map merging code introduced in the merge window for 6.11..

Important APIs/types/functions: test tags `auto quick send compress`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_btrfs_send_version 2`, `_require_test`, `_require_scratch`, `_fixed_by_kernel_commit de9f46cb0044 \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `first_stream="$send_files_dir/1.send"`, `second_stream="$send_files_dir/2.send"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L22: _require_btrfs_send_version 2; L36: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L37: _scratch_mount -o compress; L42: $XFS_IO_PROG -f -c "pwrite -S 0xab 111K 30K" $SCRATCH_MNT/foo >> $seqres.full; L44: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1 >> $seqres.full; L49: $XFS_IO_PROG -c "pwrite -S 0xcd 120K 8K" $SCRATCH_MNT/foo >> $seqres.full; L90: $XFS_IO_PROG -c "pwrite -S 0xef 160K 4K" $SCRATCH_MNT/foo >> $seqres.full; L92: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2 >> $seqres.full; L98: $BTRFS_UTIL_PROG send --compressed-data -q -f $first_stream $SCRATCH_MNT/snap1; L99: $BTRFS_UTIL_PROG send --compressed-data -q -f $second_stream \; L102: _scratch_unmount; L103: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L104: _scratch_mount; L106: $BTRFS_UTIL_PROG receive -q -f $first_stream $SCRATCH_MNT; L107: $BTRFS_UTIL_PROG receive -q -f $second_stream $SCRATCH_MNT.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; visible subtest labels include Checksums in the original filesystem:; Checksums in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/312 -->
