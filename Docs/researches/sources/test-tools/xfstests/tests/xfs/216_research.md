<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216 -->
# sources/test-tools/xfstests/tests/xfs/216

## Purpose
`sources/test-tools/xfstests/tests/xfs/216` is a reflink and copy-on-write regression. log size mkfs test - ensure the log size scaling works for small filesystems Decide which golden output file we're using.  Starting with mkfs.xfs 5.15, the default minimum log size was raised to 64MB for all cases, so we detect that by test-formatting with a 512M filesystem.  This is a little handwavy, but it's the best we can do. make large holey file make loopback mount dir walk over standard sizes (up to 256GB). The `_begin_fstest` declaration is `log metadata auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `choose_golden_output`, `_do_mkfs`. Requirement gates: `_require_scratch`, `_require_loop`. Important external or harness commands observed in the full source include `mkfs`, `mount`. Notable scenario variables include `LOOP_IMG=$SCRATCH_MNT/test_fs`, `LOOP_MNT=$SCRATCH_MNT/test_fs_dir`.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
variant configuration `sources/test-tools/xfstests/tests/xfs/216.cfg`; stable progress labels including `echo -n "fssize=${i}g "`, `echo "test write" > $LOOP_MNT/test`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 81 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/216 -->
