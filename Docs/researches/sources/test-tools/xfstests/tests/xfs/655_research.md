<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/655 -->
# sources/test-tools/xfstests/tests/xfs/655

## Purpose
`sources/test-tools/xfstests/tests/xfs/655` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, realtime-device coverage, I/O or media-error handling, directory tree and parent-pointer repair. Corrupt some metadata and try to access it with the health monitoring program running. Check that healthmon observes a metadata error. The `_begin_fstest` declaration is `auto quick eio selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `_cleanup`, `check_healthmon`. Requirement and regression gates include `_require_scratch_nocheck`, `_require_scratch_xfs_crc # can't detect minor corruption w/o crc`, `_require_xfs_io_command healthmon`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `xfs_scrub`, `mount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, runs online scrub/repair or xfs_scrub in selected modes, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/655.out`; stable progress/output labels such as `echo "Format and mount"`, `echo "Runtime corruption detection"`, `echo "Scrub corruption detection"`; diagnostic detail appended to `$seqres.full`. The source has 98 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/655 -->
