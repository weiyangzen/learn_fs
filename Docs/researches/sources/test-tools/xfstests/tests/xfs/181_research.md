<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/181 -->
# sources/test-tools/xfstests/tests/xfs/181

## Purpose
`sources/test-tools/xfstests/tests/xfs/181` is a log recovery or log-geometry regression. Like 121 only creating large EAs As part of the iunlink processing in recovery it will call VN_RELE which will inactivate the inodes and if they have EAs (which they will here) also call xfs_inactive_attrs. We want to test out this xfs_inactive_attrs code being called in recovery. Override the default cleanup function. num_files must be greater than 64 (XFS_AGI_UNLINKED_BUCKETS) so that there will be at least one linked list from one of. The `_begin_fstest` declaration is `shutdown log auto quick`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/log`. Local helper surface: `_cleanup`. Requirement gates: `_require_scratch`. Important external or harness commands observed in the full source include `mkfs`, `mount`, `xfs_inactive_attrs`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
golden output can drift when xfsprogs diagnostics, filters, or common fstests helpers change; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/181.out`; stable progress labels including `echo "mkfs"`, `echo "mount"`, `echo "open and unlink $num_files files with EAs"`, `echo "godown"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/181 -->
