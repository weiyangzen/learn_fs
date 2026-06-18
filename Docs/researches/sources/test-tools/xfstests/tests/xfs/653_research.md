<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/653 -->
# sources/test-tools/xfstests/tests/xfs/653

## Purpose
`sources/test-tools/xfstests/tests/xfs/653` is an XFS fstests shell case focused on realtime-device coverage, mount-option behavior. Tests that mkfs for a zoned file system rounds realtime subvolume sizes up to the zone size to create mountable file systems. The `_begin_fstest` declaration is `auto quick realtime growfs zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/zoned`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_test`, `_require_loop`, `_require_xfs_io_command "truncate"`, `_require_fs_space $TEST_DIR $((aligned_size / 1024))`. Important external or harness tools detected in the full source include `xfs_io`, `mount`, `umount`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/653.out`; stable progress/output labels such as `echo "Formatting file system (unaligned specified size)"`, `echo "Formatting file system (unaligned device)"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 66 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/653 -->
