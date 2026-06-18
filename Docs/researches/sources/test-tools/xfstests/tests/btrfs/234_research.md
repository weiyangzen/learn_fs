# sources/test-tools/xfstests/tests/btrfs/234

## Purpose
Test cases where a direct IO write, with O_DSYNC, can not be done and has to fallback to a buffered write. Create a test file with compression enabled (chattr +c). Now do a buffered write to create compressed extents. Now do the direct IO write with O_DSYNC into a file range that contains compressed extents. It should fallback to buffered IO and succeed. Now try doing a direct IO write, with O_DSYNC, for a range that starts with non-aligned offset. It should also fallback to buffered IO and succeed. Unmount, mount again, and verify we have the expected data. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress rw`. Requirement and capability gates: line 16: `_require_scratch`; line 17: `_require_odirect`; line 18: `_require_btrfs_no_nodatacow`; line 19: `_require_chattr c`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 16: `_require_scratch`; line 17: `_require_odirect`; line 18: `_require_btrfs_no_nodatacow`; line 19: `_require_chattr c`; line 21: `_scratch_mkfs >>$seqres.full 2>&1`; line 22: `_scratch_mount`; line 25: `touch $SCRATCH_MNT/foo`; line 29: `$XFS_IO_PROG -s -c "pwrite -S 0xab -b 1M 0 1M" $SCRATCH_MNT/foo | _filter_xfs_io`; line 33: `$XFS_IO_PROG -d -s -c "pwrite -S 0xcd 512K 512K" $SCRATCH_MNT/foo | _filter_xfs_io`; line 37: `$XFS_IO_PROG -f -d -s -c "pwrite -S 0xef 1111 512K" $SCRATCH_MNT/bar | _filter_xfs_io`; line 40: `_scratch_cycle_mount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress rw`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 234 | wrote 1048576/1048576 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 524288/524288 bytes at offset 524288 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 524288/524288 bytes at offset 1111 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | File foo data: | ... (21 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
