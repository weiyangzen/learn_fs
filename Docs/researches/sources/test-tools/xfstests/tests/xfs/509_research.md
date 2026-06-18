<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/509 -->
# sources/test-tools/xfstests/tests/xfs/509

## Purpose

Use the xfs_io bulkstat utility to verify bulkstat finds all inodes in a filesystem.  Test under various inode counts, inobt record layouts and bulkstat batch sizes.  Test v1 and v5 ioctls explicitly, as well as the ioctl version autodetection code in libfrog. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto ioctl` and imports common modules: `preamble`, `filter`. Local helper functions: `bstat_compare`, `bstat_count`, `bstat_perag_count`, `bstat_test`, `bstat_versions`, `count_metadir_files`, `inumbers_ag`, `inumbers_count`, `inumbers_fs`. Key environment variables or shell state names include `DIRCOUNT`, `INOCOUNT`, `METADATA_FILES`, `bs_root`, `bs_root_out`, `expect`, `has_v5`, `nr`, `stat_root`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_io_command bulkstat`, `_require_xfs_io_command bulkstat_single`, `_require_xfs_io_command inumbers`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `echo "$tag($v_tag): passing \"$v_flag\" to bulkstat" >> $seqres.full`, `echo -n "bulkstat $tag($v_tag): "`, `$XFS_IO_PROG -c "bulkstat -n $batchsize $v_flag" $SCRATCH_MNT | grep ino | wc -l`, `local agcount=$(_xfs_mount_agcount $SCRATCH_MNT)`, `$XFS_IO_PROG -c "bulkstat -a $ag -n $batchsize $v_flag" $SCRATCH_MNT`, `$XFS_IO_PROG -c "inumbers -a $ag -n $batchsize $v_flag" $mount`, `$XFS_IO_PROG -c "inumbers $v_flag" "$dir" | grep alloccount | \`, `_scratch_cycle_mount`; plus 8 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 509`; `expect 2057`; `bulkstat 4096 all(default): 2057`; `bulkstat 4096 all(v1): 2057`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/509 -->
