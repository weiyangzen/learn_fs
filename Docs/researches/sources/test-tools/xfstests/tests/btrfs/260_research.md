# sources/test-tools/xfstests/tests/btrfs/260

## Purpose
Make sure "btrfs filesystem defragment" can still convert the compression algorithm of all regular extents. Override the default cleanup function. _cleanup() { cd / rm -r -f $tmp.* } Unlike file extents whose btrfs specific attributes need to be grabbed from. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag compress prealloc fiemap`. Requirement and capability gates: line 22: `_require_scratch`; line 23: `_require_xfs_io_command "fiemap" "ranged"`; line 24: `_require_xfs_io_command "falloc"`; line 25: `_require_btrfs_command inspect-internal dump-tree`; line 79: `_require_btrfs_support_sectorsize 4096`. Local helper surface: `get_inode_number()` (line 27), `get_file_extent()` (line 34), `check_file_extent()` (line 45), `check_hole()` (line 62). Important command/API calls include line 24: `_require_xfs_io_command "falloc"`; line 25: `_require_btrfs_command inspect-internal dump-tree`; line 41: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t 5 $SCRATCH_DEV | grep -A4 "$file_extent_key"`; line 45: `check_file_extent()`; line 62: `check_hole()`; line 81: `_scratch_mkfs -s 4k >> $seqres.full 2>&1`; line 84: `_scratch_mount -o compress=lzo`; line 87: `$XFS_IO_PROG -f -c "pwrite 0 1m" "$SCRATCH_MNT/large" >> $seqres.full`; line 93: `$XFS_IO_PROG -f -c "pwrite 0 16k" -c "pwrite 32k 16k" -c "pwrite 64k 16k" "$SCRATCH_MNT/fragment" >> $seqres.full`; line 100: `$XFS_IO_PROG -c "falloc 16k 16k" "$SCRATCH_MNT/fragment"`; line 106: `check_file_extent "$SCRATCH_MNT/large" 0 "compression 2"`; line 109: `check_file_extent "$SCRATCH_MNT/fragment" 0 "compression 2"`; line 112: `check_file_extent "$SCRATCH_MNT/fragment" 16384 "type 2"`; line 115: `check_file_extent "$SCRATCH_MNT/fragment" 32768 "compression 2"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag compress prealloc fiemap`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 260 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
