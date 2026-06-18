<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/648 -->
# sources/test-tools/xfstests/tests/xfs/648

## Purpose
`sources/test-tools/xfstests/tests/xfs/648` is an XFS fstests shell case focused on quota enforcement. Test that XFS can set quota project ID on special files The `_begin_fstest` declaration is `auto quota`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`, `./common/quota`. Local helper surface: `create_af_unix`, `filter_quota`. Requirement and regression gates include `_require_scratch`, `_require_xfs_quota`, `_require_test_program "af_unix"`, `_require_test_program "file_attr"`, `_require_symlinks`, `_require_mknod`, `_require_file_attr`, `_require_file_attr_special`. Important external or harness tools detected in the full source include `mkfs.xfs`, `xfs_quota`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, sets up quota state and validates accounting or enforcement. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; quota tests depend on user/group setup, mount options, and stable quota-tools output.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/648.out`; diagnostic detail appended to `$seqres.full`. The source has 74 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/648 -->
