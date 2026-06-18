<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/616 -->
# sources/test-tools/xfstests/tests/xfs/616

## Purpose
`sources/test-tools/xfstests/tests/xfs/616` is an XFS fstests shell case focused on realtime-device coverage, extent mapping and exchange. Make sure that the XFS_EXCHANGE_RANGE_FILE1_WRITTEN actually skips holes and unwritten extents on the data device and the rt device when the rextsize is 1 fsblock. The `_begin_fstest` declaration is `auto fiexchange`. The file is part of the xfstests `tests/xfs` suite and exercises kernel/xfsprogs behavior through the standard fstests harness.

## Important APIs, Types, And Functions
The script is bash built on `./common/preamble` and imports `./common/filter`, `./common/preamble`. Local helper surface: `swap_and_check_contents`. Requirement and regression gates include `_require_xfs_io_command "falloc"`, `_require_xfs_io_command exchangerange`, `_require_scratch`. Important external or harness tools detected in the full source include `xfs_io`, `mkfs.xfs`, `md5sum`, `mount`. Scenario variables and harness state referenced include `SCRATCH_MNT`.

## Control Flow
The test starts with fstests setup, requirement gating, and scratch/test environment preparation. Its concrete flow formats the scratch or loop filesystem, mounts, unmounts, or cycle-mounts to test persistence across remounts, uses `xfs_io` commands for writes, fallocate/punch, bmap inspection, scrub, repair, exchange, or media verification, uses checksum/stat comparisons as the content oracle. Branches are mostly feature skips, helper return-code checks, and scenario loops over corruption targets, geometry variants, or repair modes when present. Output is compared with the companion `.out` file when one exists, with noisy paths and variable values normalized by filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch or test filesystem contents, temporary `$tmp.*` files, `$seqres.full` diagnostics, mount state, and any on-disk XFS metadata intentionally created or damaged during the test. Cleanup is handled through local `_cleanup`/`_register_cleanup` hooks when present and otherwise by the fstests harness. Remounts, syncs, offline repair, and post-test checks are used to verify that repaired metadata and file data survive persistence boundaries.

## Dependencies And Integration Points
The file integrates with fstests variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, `$here`, `$tmp`, and tool variables for xfs_io, xfs_db, xfs_repair, mkfs.xfs, xfs_scrub, quota, healer, and auxiliary test programs when referenced. Requirement gates are the compatibility contract for kernel features, xfsprogs commands, scratch-device geometry, realtime devices, quotas, loop devices, dm-error targets, and helper binaries.

## Risks
the test assumes fstests scratch/test device isolation and can leave deliberately corrupted metadata until cleanup or repair finishes; realtime-device paths depend on allocation unit and feature configuration, so tests skip or change behavior when geometry is unsuitable.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/616.out`; stable progress/output labels such as `echo "swap $tag" >> $seqres.full`, `echo "$a: md5 $a_md5_before -> $a_md5_after in $tag"`, `echo "$b: md5 $b_md5_before -> $b_md5_after in $tag"`, `echo Silence is golden`; diagnostic detail appended to `$seqres.full`; feature-dependent skips through `_notrun`; content/stat comparisons with md5sum or diff. The source has 71 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/616 -->
