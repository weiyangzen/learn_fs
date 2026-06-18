# sources/test-tools/xfstests/tests/btrfs/256

## Purpose
Test that defragging files with very small sizes works and does not result in any crash, hang or corruption. The regression is fixed by a patch with the following subject: "btrfs: fix too long loop when defragging a 1 byte file" Test file sizes of 0, 1, 512, 1K, 2K, 4K, 8K, 16K, 32K and 64K bytes. Create the files and compute their checksums. Compute the checksums. Now defrag each file. Verify the checksums after the defrag operations. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_fssum`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_fssum`; line 28: `_scratch_mkfs >> $seqres.full 2>&1`; line 29: `_scratch_mount`; line 31: `checksums_file="$TEST_DIR/btrfs-test-$seq-checksums"`; line 40: `$XFS_IO_PROG -f -c "pwrite -S $byte 0 $sz" "$SCRATCH_MNT/f_$sz" >> $seqres.full`; line 44: `$FSSUM_PROG -A -f -w "$checksums_file" "$SCRATCH_MNT"`; line 51: `$BTRFS_UTIL_PROG filesystem defragment "$SCRATCH_MNT/f_$sz" > /dev/null`; line 55: `$FSSUM_PROG -r "$checksums_file" "$SCRATCH_MNT"`; line 59: `_scratch_cycle_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io, fssum. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 256 | OK | OK`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
