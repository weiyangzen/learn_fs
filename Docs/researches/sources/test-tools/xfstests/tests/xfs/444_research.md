<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/444 -->
# sources/test-tools/xfstests/tests/xfs/444

## Purpose

Make sure XFS can fix a v5 AGFL that wraps over the last block. Refer to commit 96f859d52bcb ("libxfs: pack the agfl header structure so XFS_AGFL_SIZE is correct") for details on the original on-disk format error and the patch "xfs: detect agfl count corruption and reset agfl") for details about the fix. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick prealloc` and imports common modules: `preamble`, `filter`. Local helper functions: `dump_ag0`, `filter_agfl_reset_printk`, `mount_loop`, `runtest`. Key environment variables or shell state names include `agfl_size`, `bad_agfl_size`, `blksz`, `bno`, `bno_maxrecs`, `cmd`, `dest_pos`, `filesz`, `flcount`, `flfirst`; plus 6 more.

Requirements and feature gates: `_require_check_dmesg`, `_require_scratch`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "falloc"`, `_require_xfs_db_write_array`, `_require_scratch_xfs_crc`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `if ! _try_scratch_mount >> $seqres.full 2>&1; then`, `$XFS_IO_PROG -f -c "falloc 0 $filesz" $SCRATCH_MNT/a >> $seqres.full 2>&1`, `test -e $SCRATCH_MNT/a && $here/src/punch-alternating $SCRATCH_MNT/a`, `_scratch_unmount 2>&1 | _filter_scratch`, `_scratch_xfs_db -c 'sb 0' -c 'p' -c 'agf 0' -c 'p' -c 'agfl 0' -c 'p'`, `_scratch_mkfs >> $seqres.full`, `sectsize=$(_scratch_xfs_get_metadata_field "sectsize" "sb 0")`, `flfirst=$(_scratch_xfs_get_metadata_field "flfirst" "agf 0")`; plus 9 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 444`; `TEST fix_end`; `TEST fix_start`; `TEST fix_wrap`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/444 -->
