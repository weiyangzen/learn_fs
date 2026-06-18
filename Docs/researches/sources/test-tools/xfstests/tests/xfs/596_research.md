<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/596 -->
# sources/test-tools/xfstests/tests/xfs/596

## Purpose

growfs QA tests - repeatedly fill/grow the rt volume of the filesystem check the filesystem contents after each operation.  This is the rt equivalent of xfs/041. This is the realtime-device equivalent of a growfs fill-and-verify test. It repeatedly fills the filesystem, grows the realtime volume to specific sizes, remounts, and checks the file manifest.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest growfs ioctl auto` and imports common modules: `preamble`, `filter`. Local helper functions: `_cleanup`, `_fill`. Key environment variables or shell state names include `_do_die_on_error`, `grow_size`, `onemeginblocks`, `rtsize`.

Requirements and feature gates: `_require_scratch`, `_require_realtime`, `_require_no_large_scratch_dev`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_unmount`, `_scratch_unmount 2>/dev/null`, `"$here/src/fill2fs --verbose --dir=$1 --seed=0 --filesize=65536 --stddev=32768 --list=- >>$tmp.manifest"`, `_scratch_mkfs_xfs -rsize=${rtsize}m | _filter_mkfs 2> "$tmp.mkfs" >> $seqres.full`, `_scratch_mount`, `_xfs_force_bdev realtime $SCRATCH_MNT`, `_do "Grow filesystem to ${size}m" "xfs_growfs -R $grow_size $SCRATCH_MNT"`, `_do "_scratch_unmount"`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is realtime scratch devices, `xfs_growfs -R`, fill2fs/fill2fs_check manifests, non-zoned constraints, and forced realtime allocation. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is capacity and geometry sensitivity: realtime extents, zoned-device alignment, and manifest durability must line up or the test can fail before exercising growfs correctness. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 596`; `Make 32 megabyte rt filesystem on SCRATCH_DEV and mount... done`; `Fill filesystem... done`; `Grow filesystem to 33m... done`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/596 -->
