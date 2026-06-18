# sources/test-tools/xfstests/tests/btrfs/250

## Purpose
Test that if we write to a range of a NOCOW file that has allocated extents and there is not enough available free space for allocating new data extents, the write succeeds. Test for direct IO and buffered IO writes. The patch that fixes the direct IO case has the following subject: "btrfs: fix ENOSPC failure when attempting direct IO write into NOCOW range" Use a small fixed size filesystem so that it's quick to fill it up. Make sure the fs size is > 256M, so that the mixed block groups feature is not enabled by _scatch_mkfs_sized(), because we later want to not have more space available for allocating data extents but still have enough metadata. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick enospc`. Requirement and capability gates: line 25: `_require_scratch`; line 26: `_require_chattr C`; line 27: `_require_odirect`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 20: `rm -r -f $tmp.*`; line 25: `_require_scratch`; line 26: `_require_chattr C`; line 27: `_require_odirect`; line 35: `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`; line 36: `_scratch_mount`; line 39: `touch $SCRATCH_MNT/foobar`; line 47: `$XFS_IO_PROG -c "pwrite -S 0xab -b 1M 0 900M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 53: `$XFS_IO_PROG -d -c "pwrite -S 0xcd -b 10M 0 10M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 59: `$XFS_IO_PROG -c "pwrite -S 0xef -b 10M 10M 10M" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 63: `_scratch_cycle_mount`; line 67: `echo "File data after mounting again the filesystem:"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick enospc`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 250 | Creating test file with initial data... | wrote 943718400/943718400 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Trying direct IO write over allocated space... | wrote 10485760/10485760 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | Trying buffered IO write over allocated space... | ... (18 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
