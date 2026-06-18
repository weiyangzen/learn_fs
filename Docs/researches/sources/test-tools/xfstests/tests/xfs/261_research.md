<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/261 -->
# sources/test-tools/xfstests/tests/xfs/261

## Purpose
`sources/test-tools/xfstests/tests/xfs/261` is a quota behavior regression. This test exercises an issue in libxcmd where a problem with any mount point or project quota directory causes the program to exit complete.  The effect of this is that one cannot operate on any directory, even if the problem directory is completely unrelated to the directory one wants to operate on. Override the default cleanup function. Just use the current mount table as an example mtab file.  Odds are good there's nothing wrong with it. The `_begin_fstest` declaration is `auto quick quota`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `_cleanup`, `_setup_my_mtab`, `_perturb_my_mtab`, `_check`. Requirement gates: `_require_quota`, `_require_scratch`. Important external or harness commands observed in the full source include `mount`, `quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/261.out`; stable progress labels including `echo "Silence is golden."`, `echo print | $XFS_QUOTA_PROG -t "${my_mtab}" > /dev/null || exit`, `echo print | $XFS_QUOTA_PROG -t "${my_mtab}" > /dev/null || exit`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 95 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/261 -->
