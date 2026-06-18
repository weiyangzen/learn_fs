<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/260 -->
# sources/test-tools/xfstests/tests/xfs/260

## Purpose
`sources/test-tools/xfstests/tests/xfs/260` is a mkfs option/geometry regression. Verify that an attempt to create a too-small device with stripe geometry, is handled gracefully instead of hitting an assert in align_ag_geometry() This test verifies the problem fixed in xfsprogs with commit (mkfs.xfs: fix ASSERT on too-small device with stripe geometry) Override the default cleanup function. The `_begin_fstest` declaration is `auto quick mkfs`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/260.out`; stable progress labels including `echo 'Silence is golden'`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 41 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/260 -->
