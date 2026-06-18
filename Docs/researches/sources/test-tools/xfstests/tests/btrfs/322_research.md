<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/322 -->
# sources/test-tools/xfstests/tests/btrfs/322

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/322_research.md`.

Source read: 109 lines, SHA256 prefix `68099fed857d6ba9`.

Purpose: FS QA Test 322 Test that doing an incremental send with a file that had its size decreased and became the destination for a clone operation of an extent with an unaligned end offset that matches the new file size, works correctly..

Important APIs/types/functions: test tags `auto quick send clone fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch # for _filter_fiemap_flags`; requirements/fixed gates `_require_test`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`, `_require_xfs_io_command "reflink"`, `_require_odirect`, `_fixed_by_kernel_commit fa630df665aa \`; helper functions `_cleanup()`, `check_all_extents_shared()`; key variables `fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags)`, `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `full_send_stream=$send_files_dir/full_snap.stream`, `inc_send_stream=$send_files_dir/inc_snap.stream`, `last_extent_size=$((128 * 1024 + 5))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `check_all_extents_shared()`. Representative operation sequence: L12: _begin_fstest auto quick send clone fiemap; L23: . ./common/punch # for _filter_fiemap_flags; L26: _require_scratch_reflink; L27: _require_xfs_io_command "fiemap"; L37: local fiemap_output; L39: fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags); L54: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L55: _scratch_mount; L60: $XFS_IO_PROG -f -d -c "pwrite -S 0xab -b 128K 0 128K" \; L66: $XFS_IO_PROG -f -c "pwrite -b 0xef 0 1M" $SCRATCH_MNT/bar | _filter_xfs_io; L69: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1; L70: $BTRFS_UTIL_PROG send -f $full_send_stream $SCRATCH_MNT/snap1 >> $seqres.full 2>&1; L73: $XFS_IO_PROG -c "truncate 0" \; L77: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2; L78: $BTRFS_UTIL_PROG send -p $SCRATCH_MNT/snap1 -f $inc_send_stream \; L82: md5sum $SCRATCH_MNT/snap1/foo | _filter_scratch; L83: md5sum $SCRATCH_MNT/snap1/bar | _filter_scratch; L84: md5sum $SCRATCH_MNT/snap2/foo | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Creating snapshot and the full send stream for it...; Creating another snapshot and the incremental send stream for it...; File digests in the original filesystem:; Creating a new filesystem to receive the send streams...; File digests in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/322 -->
