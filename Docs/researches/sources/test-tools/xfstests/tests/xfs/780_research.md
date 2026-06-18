<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/780 -->
# sources/test-tools/xfstests/tests/xfs/780

## Purpose
`sources/test-tools/xfstests/tests/xfs/780` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement. Populate a XFS filesystem and fuzz every group dquot field. Try online repair and, if necessary, offline repair, to test the most likely usage pattern. The `_begin_fstest` declaration is `dangerous_fuzzers scrub repair fuzzers_bothrepair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/populate`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_xfs_fuzz_fields`, `_require_quota`. Important external or harness tools detected in the full source include `mount`. Scenario variables and harness state referenced include `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/780.out`; stable progress/output labels such as `echo "Format and populate"`, `echo "Fuzz group $id dquot"`, `echo "Done fuzzing dquot"`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 43 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/780 -->
