<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/325 -->
# sources/test-tools/xfstests/tests/btrfs/325

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/325_research.md`.

Source read: 83 lines, SHA256 prefix `34d291795a4368ec`.

Purpose: FS QA Test 325 Test that defrag merges adjacent extents that are contiguous..

Important APIs/types/functions: test tags `auto quick preallocrw defrag`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_btrfs_command inspect-internal dump-tree`, `_require_xfs_io_command "falloc"`, `_require_no_compress`, `_fixed_by_kernel_commit a0f062539085 \`, `_fixed_by_kernel_commit 77b0d113eec4 \`; helper functions `count_file_extent_items()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `count_file_extent_items()`. Representative operation sequence: L15: _require_btrfs_command inspect-internal dump-tree; L16: _require_xfs_io_command "falloc"; L33: _scratch_unmount; L34: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV | \; L36: _scratch_mount; L39: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L40: _scratch_mount; L45: $XFS_IO_PROG -f -c "falloc 0 64K" \; L47: -c "falloc 64K 64K" \; L49: -c "falloc 128K 64K" \; L51: -c "falloc 192K 64K" \; L64: $BTRFS_UTIL_PROG filesystem defragment -t 128K $SCRATCH_MNT/foo; L73: $BTRFS_UTIL_PROG filesystem defragment -t 256K $SCRATCH_MNT/foo.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: fiemap extent layout and flags; btrfs on-disk tree inspection; visible subtest labels include File data after defrag:.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/325 -->
