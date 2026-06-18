<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/656 -->
# sources/test-tools/xfstests/tests/xfs/656

## Purpose
`sources/test-tools/xfstests/tests/xfs/656` is an XFS fstests shell case focused on realtime-device coverage, I/O or media-error handling. Attempt to read and write a file in buffered and directio mode with the health monitoring program running. Check that healthmon observes all four types of IO errors. The `_begin_fstest` declaration is `auto quick eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/dmerror`, `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `filter_healer_errors`. Requirement and regression gates include `_require_scratch_nocheck`, `_require_xfs_io_command healthmon`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT 65536`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `dm-error`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/656.out`; stable progress/output labels such as `echo "Format and mount"`; diagnostic detail appended to `$seqres.full`. The source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/656 -->
