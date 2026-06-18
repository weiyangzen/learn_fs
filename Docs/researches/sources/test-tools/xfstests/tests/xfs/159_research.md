<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/159 -->
# sources/test-tools/xfstests/tests/xfs/159

## Purpose
`sources/test-tools/xfstests/tests/xfs/159` is a XFS feature-upgrade regression. Check that the xfs_db timelimit command prints the ranges that we expect. This in combination with an xfs_ondisk.h build time check in the kernel ensures that the kernel agrees with userspace. Override the default cleanup function. Format filesystem without bigtime support and populate it. The `_begin_fstest` declaration is `auto quick bigtime`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_xfs_db_command timelimit`. Important external or harness commands observed in the full source include `xfs_db`, `xfs_ondisk`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; uses xfs_db to inspect or perturb low-level metadata. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, on-disk metadata fields modified for corruption testing. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/159.out`; stable progress labels including `echo classic xfs timelimits`, `echo bigtime xfs timelimits`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/159 -->
