<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/649 -->
# sources/test-tools/xfstests/tests/xfs/649

## Purpose
`sources/test-tools/xfstests/tests/xfs/649` is an XFS fstests shell case focused on extent mapping and exchange, attribute fork repair, dump/restore behavior. Regression test for panic following IO error when reading extended attribute blocks The `_begin_fstest` declaration is `auto quick attr`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/attr`, `./common/preamble`, `./common/scsi_debug`. Local helper surface: `_cleanup`, `test_attr`. Requirement and regression gates include `_fixed_by_kernel_commit ae668cd567a6 "xfs: do not propagate ENODATA disk errors into xattr code"`, `_require_scratch_nocheck`, `_require_scsi_debug "medium_error_start"`, `_require_attrs user`. Important external or harness tools detected in the full source include `xfs_io`, `xfs_db`, `mkfs.xfs`, `setfattr`, `mount`, `stat`. Scenario variables and harness state referenced include `MOUNT_OPTIONS`, `SCRATCH_MNT`, `SCRATCH_DEV`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses `xfs_db` or fuzz helpers to inspect or intentionally corrupt on-disk metadata, sets extended attributes or validates attr-fork behavior, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/649.out`; stable progress/output labels such as `echo "SCSI debug device $scsi_debug_dev" >>$seqres.full`, `echo Block size $block_size >> $seqres.full`, `echo Inode size $inode_size >> $seqres.full`, `echo $scsi_debug_opt_noerror > /sys/module/scsi_debug/parameters/opts`, `echo -e "\nTesting : $test" >> $seqres.full`, and 10 more; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`. The source has 140 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/649 -->
