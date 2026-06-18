<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/786 -->
# sources/test-tools/xfstests/tests/xfs/786

## Purpose
`sources/test-tools/xfstests/tests/xfs/786` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair. Populate a XFS filesystem and fuzz every inobt key/pointer field. Use xfs_scrub to fix the corruption. The `_begin_fstest` declaration is `dangerous_fuzzers scrub fuzzers_online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`. Important external or harness tools detected in the full source include none. Scenario variables and harness state referenced include none.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/786.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz inobt"`, `echo "Done fuzzing inobt"`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions. The source has 34 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/786 -->
