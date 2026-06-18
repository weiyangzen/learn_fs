<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/236 -->
# sources/test-tools/xfstests/tests/xfs/236

## Purpose
`sources/test-tools/xfstests/tests/xfs/236` is a reflink and copy-on-write regression. Ensure that we can create enough distinct rmapbt entries to force creation of a multi-level rmap btree.  Delete and recreate a few times to exercise the rmap btree grow/shrink functions. Override the default cleanup function. The `_begin_fstest` declaration is `auto rmap punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`. Requirement gates: `_require_xfs_scratch_rmapbt`, `_require_xfs_io_command "fpunch"`. Important external or harness commands observed in the full source include `umount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, shared extent/refcount and CoW fork metadata. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; extent-count and bmap/fiemap assertions can change with allocator behavior while data correctness remains stable; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/236.out`; stable progress labels including `echo "Create the original file blocks"`, `echo "$i: Reflink every other block"`, `echo "$i: Delete both files"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 62 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/236 -->
