<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/166 -->
# sources/test-tools/xfstests/tests/xfs/166

## Purpose
`sources/test-tools/xfstests/tests/xfs/166` is a preallocation/unwritten extent regression. FSQA Test No. 166 ->page-mkwrite test - unwritten extents and mmap assumes 1st, 3rd and 5th blocks are single written blocks, the others are unwritten. is the extent unwritten? Beginning with 5.18, some filesystems support creating large folios for the page cache.  A system with 64k pages can create 256k folios, which means that with the old file size of 1M, the last half of the file is completely. The `_begin_fstest` declaration is `rw metadata auto quick prealloc mmap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_blocks`. Requirement gates: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_congruent_file_oplen $SCRATCH_MNT $FILE_SIZE`. Important external or harness commands observed in the full source include `xfs_bmap`. Notable scenario variables include `TEST_FILE=$SCRATCH_MNT/test_file`, `TEST_PROG=$here/src/unwritten_mmap`, `FILE_SIZE=$((12 * 1048576))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/166.out`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 83 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/166 -->
