<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/556 -->
# sources/test-tools/xfstests/tests/xfs/556

## Purpose

Check xfs_scrub's media scan can actually return diagnostic information for media errors in file data extents. This file exercises XFS online scrub, health reporting, or repair-adjacent behavior. It uses the xfstests scratch device plus xfs_scrub or xfs_spaceman commands to turn metadata health into a test oracle.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick scrub eio` and imports common modules: `preamble`, `fuzzy`, `filter`, `dmerror`. Local helper functions: `_cleanup`, `filter_scrub_errors`. Key environment variables or shell state names include `awk_len_prog`, `bad_len`, `bad_sector`, `bmap_str`, `errordev`, `file_blksz`, `fs_blksz`, `kernel_sectors_per_device_lba`, `kernel_sectors_per_fs_block`, `len`; plus 5 more.

Requirements and feature gates: `_require_scratch`, `_require_scratch_xfs_crc`, `_require_scrub`, `_require_dm_target error`, `_require_xfs_scratch_non_zoned`, `_require_scratch_xfs_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs >> $seqres.full`, `_scratch_mount`, `_scratch_unmount`, `$XFS_IO_PROG -f -c "pwrite -S 0x58 0 $((4 * file_blksz))" -c "fsync" $victim >> $seqres.full`, `if _xfs_is_realtime_file $victim; then`, `if ! _xfs_has_feature $SCRATCH_MNT rtgroups; then`, `bmap_str="$($XFS_IO_PROG -c "bmap -elpv" $victim | grep "^[[:space:]]*0:")"`, `logical_block_size=`$here/src/min_dio_alignment $SCRATCH_MNT $SCRATCH_DEV``; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/fuzzy, xfs_io scrub commands, xfs_spaceman health output, scratch remounts, and feature-specific scrub prerequisites. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that online health state is cached and feature-dependent; the scripts force mount cycles or explicit scrub passes to avoid reading stale state. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 556`; `Scrub for injected media error (single threaded)`; `Unfixable Error: SCRATCH_MNT/a: media error at data offset 2FSB length 1FSB.`; `SCRATCH_MNT: unfixable errors found: 1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/556 -->
