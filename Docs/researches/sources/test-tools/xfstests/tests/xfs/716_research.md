<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/716 -->
# sources/test-tools/xfstests/tests/xfs/716

## Purpose
`sources/test-tools/xfstests/tests/xfs/716` is an XFS fstests shell case focused on online repair and scrub, extent mapping and exchange, attribute fork repair. Make sure online repair can handle rebuilding xattrs when the data fork is in btree format and we cannot just zap the attr fork. The `_begin_fstest` declaration is `auto quick online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/inject`, `./common/preamble`. Local helper surface: `_cleanup`. Requirement and regression gates include `_require_scratch`, `_require_xfs_io_error_injection "force_repair"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "repair"`, `_require_test_program "punch-alternating"`, `_require_scratch_xfs_scrub`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `setfattr`, `punch-alternating`, `mount`, `umount`, `stat`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/716.out`; stable progress/output labels such as `echo "data fork not in btree format?"`, `echo "about to start test" >> $seqres.full`, `echo "Silence is golden."`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; post-test filesystem validation. The source has 83 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/716 -->
