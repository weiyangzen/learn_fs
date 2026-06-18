<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/167 -->
# sources/test-tools/xfstests/tests/xfs/167

## Purpose
`sources/test-tools/xfstests/tests/xfs/167` is a preallocation/unwritten extent regression. FSQA Test No. 167 unwritten extent conversion test fast devices can consume disk space at a rate of 1GB every 5s via the background workload. With 50 test loops, at 1 second per loop, that means we need at least 10GB of disk space to ensure this test will not fail with ENOSPC errors. The `_begin_fstest` declaration is `rw metadata auto stress prealloc`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `workout`. Requirement gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_fs_space $SCRATCH_MNT 10485760`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include `FSSTRESS_ARGS=`_scale_fsstress_args -d $SCRATCH_MNT -p $procs -n $nops``, `TEST_FILE=$SCRATCH_MNT/test_file`, `TEST_PROG=$here/src/unwritten_sync`, `LOOPS=$((5 * $TIME_FACTOR))`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/167.out`; stable progress labels including `echo "*** test unwritten extent conversion under heavy I/O"`, `echo "     *** test done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 49 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/167 -->
