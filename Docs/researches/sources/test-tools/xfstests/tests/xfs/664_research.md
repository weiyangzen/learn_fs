<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/664 -->
# sources/test-tools/xfstests/tests/xfs/664

## Purpose
`sources/test-tools/xfstests/tests/xfs/664` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, extent mapping and exchange, directory tree and parent-pointer repair, stress concurrency, mount-option behavior. Ensure that autonomous self healing won't fix the wrong filesystem if a snapshot of the original filesystem is now mounted on the same directory as the original. The `_begin_fstest` declaration is `auto selfhealing`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `filter_mntpt`, `new_dir_unmount`. Requirement and regression gates include `_require_test`, `_require_scrub`, `_require_xfs_io_command "repair"	# online repair support`, `_require_xfs_db_command "blocktrash"`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command "$XFS_PROPERTY_PROG" "xfs_property"`, `_require_xfs_healer $mntpt --repair`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `xfs_healer`, `xfs_property`, `fsstress`, `mount`, `stat`. Scenario variables and harness state referenced include `TEST_DIR`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, starts fsstress or stress-scrub helpers to exercise concurrency, uses dm-error or healer/systemd helpers to inject and observe I/O failures, uses checksum/stat comparisons as the content oracle, uses loop devices or configuration variants to cover mount/device geometry. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; stress timing is intentionally nondeterministic, so regressions may appear as hangs, livelocks, kernel warnings, or post-test fsck failures; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries; loop-device setup must be cleaned reliably to avoid leaked mounts or stale backing files.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/664.out`; stable progress/output labels such as `echo testdata > $mntpt/a`, `echo "LOG $XFS_HEALER_PID SO FAR:" >> $seqres.full`, `echo "LOG AFTER TRYING TO POKE:" >> $seqres.full`, `echo "LOG AFTER FAILURE" >> $seqres.full`, `echo "Should have seen stale file handle complaints"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 135 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/664 -->
