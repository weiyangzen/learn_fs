<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/264 -->
# sources/test-tools/xfstests/tests/xfs/264

## Purpose
`sources/test-tools/xfstests/tests/xfs/264` is a XFS fstests regression. Test XFS EIO error handling configuration. Stop XFS from retrying to writeback forever when hit EIO. Override the default cleanup function. Disable fail_at_unmount before test EIO error handling _fail the test if we fail to set $attr to 1, because the test probably will hang in such case and block subsequent tests. start a metadata-intensive workload, but no data allocation operation. Because uncompleted new space allocation I/Os may cause XFS to shutdown. The `_begin_fstest` declaration is `auto quick mount eio`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`, `./common/filter`, `./common/dmerror`. Local helper surface: `_cleanup`, `do_test`. Requirement gates: `_require_scratch`, `_require_dm_target error`, `_require_fs_sysfs error/fail_at_unmount`, `_require_fs_sysfs error/metadata/EIO/max_retries`, `_require_fs_sysfs error/metadata/EIO/retry_timeout_seconds`. Important external or harness commands observed in the full source include `fsstress`, `mount`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow formats scratch or loop-backed XFS filesystems with scenario-specific mkfs options; mounts, remounts, or deliberately rejects mounts through fstests helpers; adds fsstress background load to expose races and ENOSPC boundaries. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
stress subtests can expose timing-sensitive failures and require enough scratch space; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/264.out`; stable progress labels including `echo -n "error/fail_at_unmount="`, `echo "$attr=$num"`, `echo "=== Test EIO/max_retries ==="`, `echo "=== Test EIO/retry_timeout_seconds ==="`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 99 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/264 -->
