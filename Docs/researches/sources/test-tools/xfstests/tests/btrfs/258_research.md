# sources/test-tools/xfstests/tests/btrfs/258

## Purpose
Make sure btrfs auto defrag can properly defrag clusters which has hole in the middle Needs 4K sectorsize, as larger sectorsize can change the file layout. Need datacow to show which range is defragged, and we're testing autodefrag Create a layout where we have fragmented extents at [0, 64k) (sync write in reserve order), then a hole at [64k, 128k) Now trigger autodefrag, autodefrag is triggered in the cleaner thread, which will be woken up by commit thread. In this subset it primarily covers mount and remount option semantics.

## Important APIs, Types, and Functions
The fstest declaration is `auto defrag quick fiemap remount`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 19: `_require_btrfs_support_sectorsize 4096`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 11: `_begin_fstest auto defrag quick fiemap remount`; line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 19: `_require_btrfs_support_sectorsize 4096`; line 21: `_scratch_mkfs >> $seqres.full`; line 25: `_scratch_mount -o datacow,autodefrag`; line 29: `$XFS_IO_PROG -f -s -c "pwrite 48k 16k" -c "pwrite 32k 16k" -c "pwrite 16k 16k" -c "pwrite 0 16k" $SCRATCH_MNT/foobar >> $seqres.full`; line 34: `old_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 36: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 44: `_scratch_remount commit=1`; line 46: `sync`; line 48: `new_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto defrag quick fiemap remount`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 258 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
