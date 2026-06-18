<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/187 -->
# sources/test-tools/xfstests/tests/xfs/187

## Purpose
`sources/test-tools/xfstests/tests/xfs/187` is a preallocation/unwritten extent regression. Regression test for commits: 9d5e8492eee0 ("xfs: adjust rt allocation minlen when extszhint > rtextsize") 676a659b60af ("xfs: retry allocations when locality-based search fails") The first bug occurs when an extent size hint is set on a realtime file. xfs_bmapi_rtalloc adjusts the offset and length of the allocation request to try to satisfy the hint, but doesn't adjust minlen to match.  If the allocator finds free space that isn't large enough to map even a single block of the original request, bmapi_write will return ENOSPC and the write fails. The `_begin_fstest` declaration is `auto quick rw realtime prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `fill_rtdev`. Requirement gates: `_require_scratch`, `_require_realtime`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`. Important external or harness commands observed in the full source include `mount`, `punch-alternating`, `xfs_bmapi_rtalloc`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/187.out`; stable progress labels including `echo "$((f * chunksizemb)) file size $f / 20"`, `echo "$((f * chunksizemb)) file size $f / $chunks"`, `echo "Format and mount"`, `echo "rtextsize_blks=$rtextsize_blks extsize=$extsize" >> $seqres.full`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 158 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/187 -->
