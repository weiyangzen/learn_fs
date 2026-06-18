<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/303 -->
# sources/test-tools/xfstests/tests/btrfs/303

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/303_research.md`.

Source read: 91 lines, SHA256 prefix `b24af37f206076dd`.

Purpose: FS QA Test 303 Test that an incremental send does not issue unnecessary writes for a sparse file that got one new extent between its previous extent and the file's size..

Important APIs/types/functions: test tags `auto quick snapshot send fiemap`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/punch # for _filter_fiemap`; requirements/fixed gates `_require_test`, `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_fixed_by_kernel_commit 5897710b28ca \`; helper functions `_cleanup()`; key variables `send_files_dir=$TEST_DIR/btrfs-test-$seq`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L11: _begin_fstest auto quick snapshot send fiemap; L21: . ./common/punch # for _filter_fiemap; L25: _require_xfs_io_command "fiemap"; L35: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L36: _scratch_mount; L38: $XFS_IO_PROG -f -c "truncate 1G" $SCRATCH_MNT/foobar; L42: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \; L46: $BTRFS_UTIL_PROG send -f $send_files_dir/1.snap \; L52: $XFS_IO_PROG -c "pwrite -S 0xab -b 64K 0 64K" \; L58: $BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \; L62: $BTRFS_UTIL_PROG send -p $SCRATCH_MNT/mysnap1 -f $send_files_dir/2.snap \; L68: _scratch_unmount; L69: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L70: _scratch_mount; L72: $BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT > /dev/null; L73: $BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null; L85: $XFS_IO_PROG -r -c "fiemap -v" $SCRATCH_MNT/mysnap2/foobar | _filter_fiemap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; creates send streams and receives them into a fresh filesystem.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: fiemap extent layout and flags; visible subtest labels include File content in the new filesystem:; File fiemap in the new filesystem:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/303 -->
