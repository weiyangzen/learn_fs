# sources/test-tools/xfstests/tests/btrfs/240

## Purpose
FSQA Test No. 240 Test a scenario where we do several partial writes into multiple preallocated extents across two transactions and with several fsyncs in between. The goal is to check that the fsyncs succeed. This scenario used to trigger an -EIO failure on the last fsync and turn the filesystem to RO mode because of a transaction abort. Override the default cleanup function. Create our test file with 2 preallocated extents. Leave a 1M hole between them to ensure that we get two file extent items that will never be merged into a. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick prealloc log`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 29: `_require_xfs_io_command "falloc"`; line 32: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_dm_target flakey`; line 29: `_require_xfs_io_command "falloc"`; line 31: `_scratch_mkfs >>$seqres.full 2>&1`; line 32: `_require_metadata_journaling $SCRATCH_DEV`; line 34: `_scratch_mount`; line 42: `$XFS_IO_PROG -f -c "falloc 0 1M" -c "falloc 3M 3M" $SCRATCH_MNT/foobar`; line 70: `$XFS_IO_PROG -c "pwrite -S 0xab 3M 1M" -c "pwrite -S 0xef 5M 1M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 77: `sync`; line 95: `$XFS_IO_PROG -c "pwrite -S 0xcd 4M 1M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 145: `$XFS_IO_PROG -c "pwrite -S 0xff 0 1M" -c "truncate 5M" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 155: `_flakey_drop_and_remount`; line 160: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick prealloc log`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 240 | wrote 1048576/1048576 bytes at offset 3145728 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 5242880 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 4194304 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 1048576/1048576 bytes at offset 0 | ... (29 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
