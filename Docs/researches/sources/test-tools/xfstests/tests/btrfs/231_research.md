# sources/test-tools/xfstests/tests/btrfs/231

## Purpose
FSQA Test No. 231 Test that when using the NO_HOLES feature, if we truncate down a file, clone a file range covering only a hole into an offset beyond the current file size, and then fsync the file, after a power failure we get the expected file content and we do not get stale data corresponding to file extents that existed before truncating the file. Override the default cleanup function. Create our test file with 3 extents of 256K and a 256K hole at offset 256K. The file has a size of 1280K. In this subset it primarily covers reflink/clone extent sharing.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick clone log replay`. Requirement and capability gates: line 27: `_require_scratch`; line 28: `_require_btrfs_fs_feature "no_holes"`; line 29: `_require_btrfs_mkfs_feature "no-holes"`; line 30: `_require_dm_target flakey`; line 33: `_require_metadata_journaling $SCRATCH_DEV`. Local helper surface: `_cleanup()` (line 17). Important command/API calls include line 21: `rm -f $tmp.*`; line 27: `_require_scratch`; line 28: `_require_btrfs_fs_feature "no_holes"`; line 29: `_require_btrfs_mkfs_feature "no-holes"`; line 30: `_require_dm_target flakey`; line 32: `_scratch_mkfs -O no-holes >>$seqres.full 2>&1`; line 33: `_require_metadata_journaling $SCRATCH_DEV`; line 35: `_scratch_mount`; line 39: `$XFS_IO_PROG -f -s -c "pwrite -S 0xab -b 256K 0 256K" -c "pwrite -S 0xcd -b 256K 512K 256K" -c "pwrite -S 0xef -b 256K 768K 256K" -c "pwrite -S 0x73 -b 256K 1024K 256K" $SCRATCH_MN`; line 48: `sync`; line 54: `$XFS_IO_PROG -c "truncate 800K" -c "fsync" $SCRATCH_MNT/foobar`; line 58: `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 256K 1024K 256K" -c "fsync" $SCRATCH_MNT/foobar | _filter_xfs_io`; line 68: `_flakey_drop_and_remount`; line 76: `_scratch_unmount`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick clone log replay`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 231 | wrote 262144/262144 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 524288 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 786432 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | wrote 262144/262144 bytes at offset 1048576 | ... (35 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
