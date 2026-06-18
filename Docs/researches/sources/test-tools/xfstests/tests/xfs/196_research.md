<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/196 -->
# sources/test-tools/xfstests/tests/xfs/196

## Purpose
`sources/test-tools/xfstests/tests/xfs/196` is a XFS fstests regression. This test stresses indirect block reservation for delayed allocation extents. XFS reserves extra blocks for deferred allocation of delalloc extents. These reserved blocks can be divided among more extents than anticipated if the original extent for which the blocks were reserved is split into multiple delalloc extents. If this scenario repeats, eventually some extents are left without any indirect block reservation whatsoever. This leads to assert failures and possibly other problems in XFS. create sequential delayed allocation. The `_begin_fstest` declaration is `auto quick rw`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/punch`, `./common/inject`. Local helper surface: no local helpers beyond the main shell flow. Requirement gates: `_require_scratch`, `_require_xfs_io_error_injection "drop_writes"`. Important external or harness commands observed in the full source include primarily fstests shell helpers. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/196.out`; stable progress labels including `echo "Silence is golden."`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 80 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/196 -->
