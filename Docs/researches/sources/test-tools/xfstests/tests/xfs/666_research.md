<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/666 -->
# sources/test-tools/xfstests/tests/xfs/666

## Purpose
`sources/test-tools/xfstests/tests/xfs/666` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Check that the xfs_healer startup service starts the per-mount xfs_healer service for the scratch filesystem. IOWs, this is basic testing for the xfs_healer systemd background services. The `_begin_fstest` declaration is `auto selfhealing unreliable_in_parallel`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/systemd`. Local helper surface: `_cleanup`, `find_healer_trace`. Requirement and regression gates include `_require_systemd_is_running`, `_require_systemd_unit_defined xfs_healer@.service`, `_require_systemd_unit_defined xfs_healer_start.service`, `_require_scratch`, `_require_scrub`, `_require_xfs_io_command "scrub"`, `_require_xfs_spaceman_command "health"`, `_require_populate_commands`, `_require_command "$XFS_HEALER_PROG" "xfs_healer"`, `_require_command $ATTR_PROG "attr"`, `_require_xfs_healer $SCRATCH_MNT`. Important external or harness tools detected in the full source include `mkfs.xfs`, `xfs_healer`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, uses dm-error or healer/systemd helpers to inject and observe I/O failures. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; device-mapper error injection is sensitive to logical block size, realtime/zoned layout, and async writeback or readahead retries.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/666.out`; stable progress/output labels such as `echo "cannot find evidence that xfs_healer is running for $path"`, `echo "Format and populate"`, `echo "Start healer on scratch FS"`, `echo "Start healer for everything"`, `echo "Restart healer for scratch FS"`, and 1 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 123 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/666 -->
