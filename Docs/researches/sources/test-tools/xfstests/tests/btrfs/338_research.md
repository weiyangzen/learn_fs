<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/338 -->
# sources/test-tools/xfstests/tests/btrfs/338

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/338_research.md`.

Source read: 93 lines, SHA256 prefix `0e13ca2dcd364f49`.

Purpose: FS QA Test 338 Test that an incremental send works after we removed directories that have large number of hardlinks for the same file (so that we have extrefs)..

Important APIs/types/functions: test tags `auto quick send`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_test`, `_require_scratch`, `_require_fssum`, `_fixed_by_kernel_commit 1fabe43b4e1a \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`, `first_stream="$send_files_dir/1.send"`, `second_stream="$send_files_dir/2.send"`, `first_fssum="$send_files_dir/snap1.fssum"`, `second_fssum="$send_files_dir/snap2.fssum"`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L37: _scratch_mkfs >> $seqres.full 2>&1 || _fail "first mkfs failed"; L38: _scratch_mount; L66: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1; L72: _btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap2; L74: _btrfs send -f $first_stream $SCRATCH_MNT/snap1; L75: _btrfs send -f $second_stream -p $SCRATCH_MNT/snap1 $SCRATCH_MNT/snap2; L77: $FSSUM_PROG -A -f -w $first_fssum $SCRATCH_MNT/snap1; L78: $FSSUM_PROG -A -f -w $second_fssum -x $SCRATCH_MNT/snap2/snap1 \; L82: _scratch_unmount; L83: _scratch_mkfs >> $seqres.full 2>&1 || _fail "second mkfs failed"; L84: _scratch_mount; L86: _btrfs receive -f $first_stream $SCRATCH_MNT; L87: _btrfs receive -f $second_stream $SCRATCH_MNT; L89: $FSSUM_PROG -r $first_fssum $SCRATCH_MNT/snap1; L90: $FSSUM_PROG -r $second_fssum $SCRATCH_MNT/snap2.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/338 -->
