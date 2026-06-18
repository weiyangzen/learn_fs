<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/310 -->
# sources/test-tools/xfstests/tests/btrfs/310

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/310_research.md`.

Source read: 76 lines, SHA256 prefix `c46b17c703d27e4f`.

Purpose: FS QA Test 310 Make sure reading on an compressed inline extent is behaving correctly.

Important APIs/types/functions: test tags `auto quick compress`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_btrfs_inline_extents_creation`, `_require_btrfs_support_sectorsize 4096`, `_fixed_by_kernel_commit e01a83e12604 \`; helper functions `workload()`; key variables `md5sum_correct="5fed275e7617a806f94c173746a2a723"`, `result=$(_md5_checksum "$SCRATCH_MNT/inline_file")`, `result=$(_md5_checksum "$SCRATCH_MNT/inline_file")`, `algo_list=($(_btrfs_compression_algos))`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `workload()`. Representative operation sequence: L16: _require_btrfs_inline_extents_creation; L17: _require_btrfs_support_sectorsize 4096; L23: md5sum_correct="5fed275e7617a806f94c173746a2a723"; L30: _scratch_mkfs >> $seqres.full; L31: _scratch_mount -o compress=${algo}; L36: if [ "$result" != "$md5sum_correct" ]; then; L43: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/inline_file | tail -n 1 > $tmp.fiemap; L44: cat $tmp.fiemap >> $seqres.full; L48: if ! grep -q "0x309" $tmp.fiemap; then; L49: rm -f -- $tmp.fiemap; L52: rm -f -- $tmp.fiemap; L55: _scratch_cycle_mount; L61: if [ "$result" != "$md5sum_correct" ]; then; L64: _scratch_unmount; L65: _check_scratch_fs; L68: algo_list=($(_btrfs_compression_algos)).

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; matching file digests before and after remount/send/receive; fiemap extent layout and flags; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/310 -->
