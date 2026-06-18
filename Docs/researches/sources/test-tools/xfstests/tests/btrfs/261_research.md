# sources/test-tools/xfstests/tests/btrfs/261

## Purpose
Make sure btrfs raid profiles can handling one corrupted device without affecting the consistency of the fs. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, scrub detection and repair paths.

## Important APIs, Types, and Functions
The fstest declaration is `auto volume raid scrub`. Requirement and capability gates: line 13: `_require_scratch_dev_pool 4`; line 15: `_require_fssum`. Local helper surface: `prepare_fs()` (line 17), `workload()` (line 46). Important command/API calls include line 11: `_begin_fstest auto volume raid scrub`; line 13: `_require_scratch_dev_pool 4`; line 14: `_btrfs_get_profile_configs replace-missing`; line 15: `_require_fssum`; line 24: `_scratch_pool_mkfs $mkfs_opts -b 1G >> $seqres.full 2>&1`; line 30: `_scratch_mount -o compress=no`; line 33: `$XFS_IO_PROG -f -c "pwrite -S 0xfe 0 400M" $SCRATCH_MNT/garbage > /dev/null 2>&1`; line 39: `sync`; line 42: `$FSSUM_PROG -A -f -w $tmp.saved_fssum $SCRATCH_MNT`; line 43: `_scratch_unmount`; line 51: `_scratch_dev_pool_get 4`; line 53: `rm -f -- $tmp.saved_fssum`; line 58: `$XFS_IO_PROG -c "pwrite 1M 1023M" $SCRATCH_DEV > /dev/null 2>&1`; line 60: `_scratch_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto volume raid scrub`, install cleanup if needed, enforce requirements, then mounts the test filesystem, runs scrub or checks scrub reports, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Multi-device tests allocate scratch pool devices and leave correctness evidence in chunk maps, device registry state, degraded mounts, and btrfs check results. Corruption is injected below the filesystem and then validated after scrub, remount, or direct device reads. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 261 | Silence is golden`.

## Risks and Edge Cases
device topology tests can expose races in device scan state, degraded mounts, stripe geometry, replacement, and cleanup of scratch device pools; scrub repair signals depend on precise logical-to-physical mapping and can miss corruption if checksum, parity, or duplicate-copy selection regresses. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
