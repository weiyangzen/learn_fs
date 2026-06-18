<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/795 -->
# sources/test-tools/xfstests/tests/xfs/795

## Purpose
`sources/test-tools/xfstests/tests/xfs/795` is an XFS fstests shell case focused on online repair and scrub, metadata fuzzing and repair, quota enforcement, extent mapping and exchange, stress concurrency. Ensure that the sysadmin won't hit EDQUOT while repairing file data contents even if the file's quota limits have been exceeded. This tests the quota reservation handling inside the exchangerange code used by repair. The `_begin_fstest` declaration is `online_repair`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/fuzzy`, `./common/inject`, `./common/preamble`, `./common/quota`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_quota`, `_require_user`, `_require_scratch`, `_require_xfs_stress_online_repair`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `xfs_quota`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; intentional metadata corruption can make failures noisy and depends on xfs_db field names matching the tested xfsprogs version; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/795.out`; stable progress/output labels such as `echo "set up quota" >> $seqres.full`, `echo "repairs" >> $seqres.full`, `echo "fail quota" >> $seqres.full`, `echo Silence is golden`; diagnostic detail appended to `$seqres.full`. The source has 75 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/795 -->
