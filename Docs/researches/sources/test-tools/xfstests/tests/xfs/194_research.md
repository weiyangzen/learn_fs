<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/194 -->
# sources/test-tools/xfstests/tests/xfs/194

## Purpose
`sources/test-tools/xfstests/tests/xfs/194` is a XFS fstests regression. Test mapping around/over holes for sub-page blocks Override the default cleanup function. Unmount the V4 filesystem we forcibly created to run this test so that the post-test wrapup checks won't try to remount the filesystem with different MOUNT_OPTIONS (specifically, the ones that get screened out by _force_xfsv4_mount_options) and fail. only xfs supported due to use of xfs_bmap This currently forces nocrc because only that can support 512 byte block size. The `_begin_fstest` declaration is `rw auto mmap`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `_filter_bmap`, `_filter_od`. Requirement gates: `_require_scratch`, `_require_xfs_nocrc`. Important external or harness commands observed in the full source include `xfs_bmap`, `xfs_io`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/194.out`; stable progress labels including `echo "== Test 1 =="`, `echo "== Test 2 =="`, `echo "== Test 3 =="`, `echo "== Test 4 =="`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 220 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/194 -->
