<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/344 -->
# sources/test-tools/xfstests/tests/btrfs/344

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/344_research.md`.

Source read: 53 lines, SHA256 prefix `2d87e04304d90d16`.

Purpose: FS QA Test 344 Check if a failed inline attempt for compression write will mark the whole inode as incompressible.

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; key variables `blocksize=$(_get_file_block_size $SCRATCH_MNT)`, `ino=$(stat -c "%i" $SCRATCH_MNT/foobar)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _require_btrfs_command inspect-internal dump-tree; L19: _scratch_mkfs >>$seqres.full 2>&1; L23: _scratch_mount "-o compress,max_inline=4"; L34: $XFS_IO_PROG -f -c "pwrite 0 $(( $blocksize / 2 ))" -c sync \; L37: _scratch_unmount; L40: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV >> $seqres.full; L43: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\; L48: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: has a placeholder fixed-by commit annotation; parses btrfs-progs textual dump output; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/344 -->
