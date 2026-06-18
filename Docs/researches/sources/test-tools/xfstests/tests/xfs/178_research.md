<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/178 -->
# sources/test-tools/xfstests/tests/xfs/178

## Purpose
`sources/test-tools/xfstests/tests/xfs/178` is a metadata repair/corruption regression. Reproduce PV#:967665 Test if mkfs.xfs wipes old AG headers when using -f option dd the 1st sector then repair dd first sector xfs_repair check repair From the PV o Summary of testing:. The `_begin_fstest` declaration is `mkfs other auto`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/repair`. Local helper surface: `filter_repair`, `_dd_repair_check`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `mkfs`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/178.out`; stable progress labels including `echo "repair passed"`, `echo "repair failed!"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 77 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/178 -->
