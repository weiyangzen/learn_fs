<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/319 -->
# sources/test-tools/xfstests/tests/btrfs/319

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/319_research.md`.

Source read: 91 lines, SHA256 prefix `3ab5bbd596fc3383`.

Purpose: FS QA Test 319 Test that a send operation will issue a clone operation for a shared extent of a file if the extent ends at the i_size of the file and the i_size is not sector size aligned. Override the default cleanup function..

Important APIs/types/functions: test tags `auto quick send clone fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/reflink`, `. ./common/punch # for _filter_fiemap_flags`; requirements/fixed gates `_require_test`, `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fiemap"`, `_require_odirect`, `_fixed_by_kernel_commit 46a6e10a1ab1 \`; helper functions `_cleanup()`, `check_all_extents_shared()`; key variables `fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags)`, `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `send_stream=$send_files_dir/snap.stream`, `file_size=$((1024 * 1024 + 5))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `check_all_extents_shared()`. Representative operation sequence: L12: _begin_fstest auto quick send clone fiemap; L24: . ./common/punch # for _filter_fiemap_flags; L27: _require_scratch_reflink; L29: _require_xfs_io_command "fiemap"; L38: local fiemap_output; L40: fiemap_output=$($XFS_IO_PROG -r -c "fiemap -v" $file | _filter_fiemap_flags); L54: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L55: _scratch_mount; L60: $XFS_IO_PROG -f -d -c "pwrite -S 0xab -b $file_size 0 $file_size" \; L67: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap; L68: $BTRFS_UTIL_PROG send -f $send_stream $SCRATCH_MNT/snap >> $seqres.full 2>&1; L71: md5sum $SCRATCH_MNT/snap/foo | _filter_scratch; L72: md5sum $SCRATCH_MNT/snap/bar | _filter_scratch; L77: _scratch_unmount; L78: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L79: _scratch_mount; L81: $BTRFS_UTIL_PROG receive -f $send_stream $SCRATCH_MNT; L84: md5sum $SCRATCH_MNT/snap/foo | _filter_scratch.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Creating snapshot and a send stream for it...; File digests in the original filesystem:; Creating a new filesystem to receive the send stream...; File digests in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/319 -->
