<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/220 -->
# sources/test-tools/xfstests/tests/xfs/220

## Purpose
`sources/test-tools/xfstests/tests/xfs/220` is a quota behavior regression. Test quota off handling. Based on bug reports from Utako Kusaka <u-kusaka@wm.jp.nec.com> and Ryota Yamauchi <r-yamauchi@vf.jp.nec.com>. Override the default cleanup function. Only mount with the specific quota options mentioned below create scratch filesystem mount  with quotas enabled turn off quota. The `_begin_fstest` declaration is `auto quota quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/quota`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`, `_require_quota`. Important external or harness commands observed in the full source include `mount`, `quota`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; configures or queries user/group/project quota state. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs, quota accounting and grace-period metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
quota output and timer calculations are sensitive to quota-tools versions, current time, and 32-bit time support; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/220.out`; stable progress labels including `echo "Silence is golden."`, `echo "freesp $before_freesp -> $after_freesp ($delta)" >> $seqres.full`, `echo "expected Q_XQUOTARM to free space"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 84 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/220 -->
