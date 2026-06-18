# sources/test-tools/xfstests/tests/btrfs/263

## Purpose
Make sure btrfs autodefrag will not defrag ranges which won't reduce defragmentation. Needs fixed 4K sector size, or the file layout will not match the expected result. Create the initial layout, with a large 64K extent for later fragments. Need to bump the generation by one, as autodefrag uses the last modified generation of a subvolume. Without this generation bump, autodefrag will defrag the whole file, not only the new write. Remount to autodefrag. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, mount and remount option semantics, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag fiemap remount`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_btrfs_support_sectorsize 4096`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto quick defrag fiemap remount`; line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap" "ranged"`; line 20: `_require_btrfs_support_sectorsize 4096`; line 22: `_scratch_mkfs >> $seqres.full`; line 24: `_scratch_mount -o noautodefrag`; line 27: `$XFS_IO_PROG -f -c "pwrite 0 64K" -c sync "$SCRATCH_MNT/foobar" >> $seqres.full`; line 32: `touch "$SCRATCH_MNT/trash"`; line 33: `sync`; line 36: `_scratch_remount autodefrag`; line 39: `$XFS_IO_PROG -c "pwrite 16K 4K" -c sync "$SCRATCH_MNT/foobar" >> $seqres.full`; line 42: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 44: `old_csum=$(_md5_checksum "$SCRATCH_MNT/foobar")`; line 50: `_scratch_remount commit=1`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag fiemap remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 263 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
