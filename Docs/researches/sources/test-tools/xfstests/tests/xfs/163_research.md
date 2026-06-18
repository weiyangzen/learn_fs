<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/163 -->
# sources/test-tools/xfstests/tests/xfs/163

## Purpose
`sources/test-tools/xfstests/tests/xfs/163` is a online grow/shrink regression. XFS shrinkfs basic functionality test This test attempts to shrink with a small size (512K), half AG size and an out-of-bound size (agsize + 1) to observe if it works as expected. If we couldn't shrink the filesystem due to lack of space, we're done with this test. agcount = 1 is forbidden on purpose, and need to ensure shrinking to 2 AGs isn't feasible yet. So agcount = 3 is the minimum number now. The `_begin_fstest` declaration is `auto quick growfs shrinkfs`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `test_shrink`. Requirement gates: `_require_scratch_xfs_shrink`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/163.out`; stable progress labels including `echo "Format and mount"`, `echo "Shrink fs (small size)"`, `echo "Shrink fs (small size) failure"`, `echo "Shrink fs (half AG)"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 70 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/163 -->
