<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/542 -->
# sources/test-tools/xfstests/tests/xfs/542

## Purpose

Test that COW writeback that overlaps non-shared delalloc blocks does not leave around stale delalloc blocks on I/O failure. This triggers assert failures and free space accounting corruption on XFS. Fixed by upstream kernel commit 5ca5916b6bc9 ("xfs: punch out data fork delalloc blocks on COW writeback failure"). This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick clone` and imports common modules: `preamble`, `reflink`, `dmflakey`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `blksz`, `len`.

Requirements and feature gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "cowextsize"`, `_require_flakey_with_error_writes`. Recorded fix annotations: `_fixed_by_kernel_commit 5ca5916b6bc9 xfs: punch out data fork delalloc blocks on COW writeback failure`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount`, `$XFS_IO_PROG -c "cowextsize $((blksz * 2))" $SCRATCH_MNT >> $seqres.full`, `$XFS_IO_PROG -fc "pwrite $blksz $blksz" $SCRATCH_MNT/file1 >> $seqres.full`, `$XFS_IO_PROG -fc "reflink $SCRATCH_MNT/file1" \`, `$XFS_IO_PROG -c "pwrite 0 $len" \`, `_scratch_unmount`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 542`; `sync_file_range: Input/output error`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/542 -->
