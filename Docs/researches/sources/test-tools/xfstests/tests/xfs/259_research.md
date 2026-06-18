<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/259 -->
# sources/test-tools/xfstests/tests/xfs/259

## Purpose
`sources/test-tools/xfstests/tests/xfs/259` is a XFS fstests regression. Test fs creation on 4 TB minus few bytes partition Override the default cleanup function. Test various sizes slightly less than 4 TB. Need to handle different minimum block sizes for CRC enabled filesystems, but use a small log so we don't write lots of zeros unnecessarily. The `_begin_fstest` declaration is `auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_test`, `_require_loop`, `_require_math`. Important external or harness commands observed in the full source include `mkfs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/259.out`; stable progress labels including `echo "Trying to make (4TB - ${del}B) long xfs, block size $bs" | \`, `echo "mkfs failed!"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 54 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/259 -->
