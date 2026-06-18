<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/201 -->
# sources/test-tools/xfstests/tests/xfs/201

## Purpose
`sources/test-tools/xfstests/tests/xfs/201` is a XFS fstests regression. Test out the infamous xfs_btree_delrec corruption. Only happens on 32-bit kernels without CONFIG_LBD, but it should be harmless to run this everywhere. Override the default cleanup function. Create a fragmented file and truncate it again. The `_begin_fstest` declaration is `metadata auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `_cleanup`, `do_pwrite`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `xfs_btree_delrec`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/201.out`; stable progress labels including `echo "*** done"`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/201 -->
