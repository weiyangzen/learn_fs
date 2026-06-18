<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/502 -->
# sources/test-tools/xfstests/tests/xfs/502

## Purpose

Stress test creating a lot of unlinked O_TMPFILE files and closing them all at once, checking that we don't blow up the filesystem.  This is sort of a performance test for the xfs unlinked inode backref patchset. Here we force the use of the slow iunlink bucket walk code, using every CPU possible. This file is part of the unlinked-inode stress coverage for O_TMPFILE and the iunlink fallback path. It opens many unlinked files, injects fallback behavior, and validates cleanup through unmount/remount.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick unlink` and imports common modules: `preamble`, `inject`, `filter`. Local helper functions: none Key environment variables or shell state names include `after`, `before`, `max_allowable_files`, `max_files`, `nr_cpus`, `testfile`.

Requirements and feature gates: `_require_xfs_io_error_injection "iunlink_fallback"`, `_require_scratch`, `_require_test_program "t_open_tmpfiles"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs $(_scratch_mkfs_concurrency_options) | _filter_mkfs 2> $tmp.mkfs > /dev/null`, `_scratch_mount`, `_scratch_inject_error "iunlink_fallback" "2"`, `$here/src/t_open_tmpfiles $SCRATCH_MNT/$i >> $seqres.full &`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the `t_open_tmpfiles` helper, error injection knobs from common/inject, scratch mkfs concurrency options, process file descriptor limits, and unlinked-list log recovery. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is resource sensitivity: file-max, ulimit, CPU count, load factor, and delayed log recovery can change runtime sharply or mask the intended iunlink fallback path. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 502`; `silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/502 -->
