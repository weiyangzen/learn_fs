<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/557 -->
# sources/test-tools/xfstests/tests/xfs/557

## Purpose

This is a test for: bf3cb3944792 (xfs: allow single bulkstat of special inodes) Create a filesystem which contains an inode with a lower number than the root inode. Then verify that XFS_BULK_IREQ_SPECIAL_ROOT gets the correct root inode number. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick prealloc` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include `bulkstat_root_inum`, `fake_inum`, `inums`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "bulkstat_single"`, `_require_scratch`. Recorded fix annotations: `_fixed_by_kernel_commit 817644fa4525 xfs: get root inode correctly at bulkstat`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs: get root inode correctly at bulkstat"`, `inums=($(_scratch_xfs_create_fake_root))`, `bulkstat_root_inum=$($XFS_IO_PROG -c 'bulkstat_single root' $SCRATCH_MNT | grep bs_ino | awk '{print $3;}')`, `echo "bulkstat_root_inum: $bulkstat_root_inum" >> $seqres.full`, `if [ $root_inum -ne $bulkstat_root_inum ]; then`, `echo "root ino mismatch: expected:${root_inum}, actual:${bulkstat_root_inum}"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 557`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/557 -->
