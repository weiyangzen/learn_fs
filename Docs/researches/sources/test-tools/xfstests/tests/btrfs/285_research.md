# sources/test-tools/xfstests/tests/btrfs/285

## Purpose
Test that mounting a btrfs filesystem properly loads block group size classes. Write files with extents in each size class Sync to force the extent allocation cycle mount to drop the block group cache Another write causes us to actually load the block groups success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick`. Requirement and capability gates: line 17: `_require_scratch`; line 18: `_require_btrfs_fs_sysfs`; line 19: `_require_fs_sysfs allocation/data/size_classes`. Local helper surface: `sysfs_size_classes()` (line 12). Important command/API calls include line 17: `_require_scratch`; line 18: `_require_btrfs_fs_sysfs`; line 19: `_require_fs_sysfs allocation/data/size_classes`; line 26: `_scratch_mkfs >/dev/null`; line 27: `_scratch_mount`; line 29: `$XFS_IO_PROG -fc "pwrite -q 0 $small" $f.small`; line 30: `$XFS_IO_PROG -fc "pwrite -q 0 $medium" $f.medium`; line 31: `$XFS_IO_PROG -fc "pwrite -q 0 $large" $f.large`; line 33: `sync`; line 37: `_scratch_cycle_mount`; line 40: `$XFS_IO_PROG -fc "pwrite -q 0 $large" $f.large.2`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 285 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
