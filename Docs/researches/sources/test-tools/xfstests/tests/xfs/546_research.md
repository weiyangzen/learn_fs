<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/546 -->
# sources/test-tools/xfstests/tests/xfs/546

## Purpose

Regression test for kernel commits: 5679897eb104 ("vfs: make sync_filesystem return errors from ->sync_fs") 2d86293c7075 ("xfs: return errors in xfs_fs_sync_fs") During a code inspection, I noticed that sync_filesystem ignores the return value of the ->sync_fs calls that it makes.  sync_filesystem, in turn is used by the syncfs(2) syscall to persist filesystem changes to disk.  This means that syncfs(2) does not capture internal filesystem errors that are neither visible from the block device (e.g. media error) nor recorded in s_wb_err. XFS historically returned 0 from ->sync_fs even if there were log failures, so that had to be corrected as well. The kernel commits above fix this problem, so this test tries to trigger the bug by using the shutdown ioctl on a clean, freshly mounted filesystem in the hope that the EIO generated as a result of the filesystem being shut down is only visible via ->sync_fs. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick shutdown` and imports common modules: `preamble`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_scratch_shutdown_and_syncfs`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mount`, `_scratch_shutdown_and_syncfs`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 546`; `syncfs: Input/output error`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/546 -->
