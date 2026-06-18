<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/602 -->
# sources/test-tools/xfstests/tests/xfs/602

## Purpose

Test using runtime code to fix unlinked inodes on a clean filesystem that never got cleaned up. This file tests runtime repair of synthesized unlinked-inode lists on a clean filesystem. It creates iunlink buckets with xfs_db, then checks recovery through normal runtime, bulkstat, and optional quotacheck paths.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick unlink` and imports common modules: `preamble`, `filter`, `fuzzy`, `quota`. Local helper functions: `__repair_check_scratch`, `exercise_scratch`, `final_check_scratch`, `format_scratch`. Key environment variables or shell state names include `IUNLINK_BUCKETLEN`, `MOUNT_OPTIONS`, `XFS_AGI_UNLINKED_BUCKETS`, `orig_mount_options`, `res`.

Requirements and feature gates: `_require_xfs_db_command iunlink`, `_require_scratch_nocheck	# we'll run repair ourselves`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -d agcount=1 | _filter_mkfs 2> "${tmp}.mkfs" >> $seqres.full`, `local nr_iunlinks="$((IUNLINK_BUCKETLEN * XFS_AGI_UNLINKED_BUCKETS))"`, `readarray -t BADINODES < <(_scratch_xfs_db -x -c "iunlink -n $nr_iunlinks" | awk '{print $4}')`, `_scratch_xfs_repair -o force_geometry -n 2>&1 | \`, `_scratch_mount`, `_scratch_unmount`, `echo "+ Part 1: See if bulkstat can recover the unlinked list" | tee -a $seqres.full`, `$XFS_IO_PROG -c 'bulkstat' $SCRATCH_MNT > /dev/null`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db `iunlink`, one-AG scratch geometry, unlinked bucket constants, bulkstat, quota mount options, and offline repair in no-modify mode as the final oracle. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that quotacheck or offline repair can clean up too early or report geometry complaints unrelated to iunlink recovery, so the script controls quota state and uses force_geometry for checking. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 602`; `+ Part 0: See if runtime can recover the unlinked list`; `+ Part 1: See if bulkstat can recover the unlinked list`; `+ Part 2: See if quotacheck can recover the unlinked list`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/602 -->
