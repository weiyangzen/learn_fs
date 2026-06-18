<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/168 -->
# sources/test-tools/xfstests/tests/xfs/168

## Purpose
`sources/test-tools/xfstests/tests/xfs/168` is a online grow/shrink regression. XFS online shrinkfs stress test This test attempts to shrink unused space as much as possible with background fsstress workload. It will decrease the shrink size if larger size fails. And totally repeat 2 * TIME_FACTOR times. fix the reserve block pool to a known size so that the enospc calculations work out correctly. -w ensures that the only ops are ones which cause write I/O shrink in chunks of this size at most. The `_begin_fstest` declaration is `auto growfs shrinkfs ioctl prealloc stress`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`. Local helper surface: `create_scratch`, `fill_scratch`, `stress_scratch`. Requirement gates: `_require_scratch_xfs_shrink`, `_require_xfs_io_command "falloc"`. Important external or harness commands observed in the full source include `fsstress`, `mkfs`, `xfs_repair`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; runs xfs_repair in checking or fixing mode and treats repair output as part of the oracle; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; online grow/shrink cases depend on free-space geometry and can skip or fail if ENOSPC behavior changes; stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/168.out`; stable progress labels including `echo "$out" | grep -q 'No space left on device' && continue`, `echo "Silence is golden"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 112 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/168 -->
