<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/606 -->
# sources/test-tools/xfstests/tests/xfs/606

## Purpose
`sources/test-tools/xfstests/tests/xfs/606` is an XFS fstests shell case focused on mount-option behavior. Test xfs_growfs with "too-small" size expansion, which lead to a delta of "0" in xfs_growfs_data_private. This's a regression test of 84712492e6da ("xfs: short circuit xfs_growfs_data_private() if delta is zero"). The `_begin_fstest` declaration is `auto quick growfs`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_fixed_by_kernel_commit 84712492e6da "xfs: short circuit xfs_growfs_data_private() if delta is zero"`, `_require_test`, `_require_loop`, `_require_xfs_io_command "truncate"`, `_require_command "$XFS_GROWFS_PROG" xfs_growfs`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/606.out`; stable progress/output labels such as `echo "xfs_growfs fails!"`, `echo "Silence is golden"`; diagnostic detail appended to `$seqres.full`. The source has 58 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/606 -->
