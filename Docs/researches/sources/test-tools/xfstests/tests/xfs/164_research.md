<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/164 -->
# sources/test-tools/xfstests/tests/xfs/164

## Purpose
`sources/test-tools/xfstests/tests/xfs/164` is a preallocation/unwritten extent regression. To test for short dio reads on IRIX and Linux - pv#962005/962547 http://bugworks.engr.sgi.com/query.cgi/962005 In particular we are interested in dio_reads for the cases of: * eof on a hole * eof on an unwritten extent * eof on a sector boundary and not on a sector boundary on a BB boundary on an odd byte boundary => 1 short of boundary. The `_begin_fstest` declaration is `rw pattern auto prealloc quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_filter_io`, `_filter_bmap`, `_test_eof_hole`, `_test_eof_unwritten_extent`. Requirement gates: `_require_test`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/164.out`; stable progress labels including `echo ""`, `echo "boundary_minus1 = $boundary_minus1"`, `echo ""`, `echo "boundary_plus1 = $boundary_plus1"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 125 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/164 -->
