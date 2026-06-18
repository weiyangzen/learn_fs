<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/669 -->
# sources/test-tools/xfstests/tests/xfs/669

## Purpose
`sources/test-tools/xfstests/tests/xfs/669` is an XFS fstests shell case focused on XFS regression coverage. Test that mounts of zoned file systems on conventional devices don't create more open zones than allowed when the last blocks in one or more zones have been invalidated. The `_begin_fstest` declaration is `auto quick zone`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/preamble`. Local helper surface: no local shell helpers beyond the main script body. Requirement and regression gates include `_require_scratch_nocheck`, `_require_odirect`, `_require_non_zoned_device $SCRATCH_DEV`. Important external or harness tools detected in the full source include `mkfs.xfs`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/669.out`; stable progress/output labels such as `echo "zone size: $zone_size_mib" >>$seqres.full`, `echo "file size: $file_size_mib" >>$seqres.full`, `echo "nr files: $nr_files" >>$seqres.full`; diagnostic detail appended to `$seqres.full`; hard failures through `_fail` assertions; feature-dependent skips through `_notrun`. The source has 68 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/669 -->
