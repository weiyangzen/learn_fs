<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/206 -->
# sources/test-tools/xfstests/tests/xfs/206

## Purpose
`sources/test-tools/xfstests/tests/xfs/206` is a reflink and copy-on-write regression. Test trim of last small AG for large filesystem resizes As reported at http://article.gmane.org/gmane.comp.file-systems.xfs.general/29187 this trimming may cause an overflow in the new size calculation. Patch and testcase at http://article.gmane.org/gmane.comp.file-systems.xfs.general/29193 Override the default cleanup function. Create a file w/ the offset we wish to resize to. The `_begin_fstest` declaration is `growfs auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `mkfs_filter`. Requirement gates: `_require_test`, `_require_loop`. Important external or harness commands observed in the full source include `mkfs`, `mount`, `umount`, `xfs_growfs`, `xfs_info`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; creates shared extents and forces copy-on-write conversions. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, loop devices and loop-mounted images, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/206.out`; stable progress labels including `echo "=== truncate file ==="`, `echo "=== mkfs.xfs ==="`, `echo "=== xfs_growfs ==="`, `echo "=== xfs_info ==="`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 93 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/206 -->
