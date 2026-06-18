<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/559 -->
# sources/test-tools/xfstests/tests/xfs/559

## Purpose

This is a regression test for a data corruption bug that existed in iomap's buffered write routines. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick rw mmap` and imports common modules: `preamble`, `inject`, `tracing`. Local helper functions: `_cleanup`, `wait_for_errortag`. Key environment variables or shell state names include `base_pagesize`, `blksz`, `blocks`, `dirty_offset`, `dirty_pageoff`, `filesz`, `max_writesize`, `saw_invalidation`, `sentryfile`, `tracefile`; plus 1 more.

Requirements and feature gates: `_require_ftrace`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_error_injection "write_delay_ms"`, `_require_scratch`, `_require_pagecache_access $SCRATCH_MNT`. Recorded fix annotations: `_fixed_by_kernel_commit 304a68b9c63b xfs: use iomap_valid method to detect stale cached iomaps`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount >> $seqres.full`, `$XFS_IO_PROG -c 'chattr -x' $SCRATCH_MNT &> $seqres.full`, `$XFS_IO_PROG -f -c "falloc 0 $filesz" $SCRATCH_MNT/file >> $seqres.full`, `_scratch_cycle_mount`, `$XFS_IO_PROG -c "pwrite -S 0x58 $dirty_offset 1" $SCRATCH_MNT/file >> $seqres.full`, `_scratch_inject_error "write_delay_ms" 500`, `_ftrace_record_events 'xfs_iomap_invalid'`; plus 4 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 559`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/559 -->
