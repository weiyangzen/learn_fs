<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/343 -->
# sources/test-tools/xfstests/tests/btrfs/343

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/343_research.md`.

Source read: 48 lines, SHA256 prefix `83f0a776d34a2d77`.

Purpose: FS QA Test 343 A regression test to make sure a single-block write at file offset 0 won't incorrectly mark the inode incompressible..

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit xxxxxxxxxxxx \`; key variables `blocksize=$(_get_file_block_size $SCRATCH_MNT)`, `ino=$(stat -c "%i" $SCRATCH_MNT/foobar)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L14: _require_btrfs_command inspect-internal dump-tree; L19: _scratch_mkfs >>$seqres.full 2>&1; L20: _scratch_mount "-o compress,max_inline=2048"; L28: $XFS_IO_PROG -f -c "truncate $((2 * $blocksize))" -c "pwrite 0 2k" -c sync \; L31: _scratch_unmount; L34: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV >> $seqres.full; L37: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\; L42: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: has a placeholder fixed-by commit annotation; parses btrfs-progs textual dump output; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/343 -->
