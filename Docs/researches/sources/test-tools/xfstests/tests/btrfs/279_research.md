# sources/test-tools/xfstests/tests/btrfs/279

## Purpose
Test that if we have two files with shared extents, after removing one of the files, if we do a fiemap against the other file, it does not report extents as shared anymore. This exercises the processing of delayed references for data extents in the backref walking code, used by fiemap to determine if an extent is shared. Create two test subvolumes, we'll reflink files between them. success, all done. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick subvol fiemap clone`. Requirement and capability gates: line 21: `_require_scratch_reflink`; line 22: `_require_cp_reflink`; line 23: `_require_xfs_io_command "fiemap"`. Local helper surface: `run_test()` (line 28). Important command/API calls include line 18: `. ./common/reflink`; line 21: `_require_scratch_reflink`; line 22: `_require_cp_reflink`; line 23: `_require_xfs_io_command "fiemap"`; line 34: `$XFS_IO_PROG -f -c "pwrite 0 64K" $file_path_1 | _filter_xfs_io`; line 35: `_cp_reflink $file_path_1 $file_path_2`; line 37: `if [ $do_sync -eq 1 ]; then`; line 38: `sync`; line 41: `echo "Fiemap of $file_path_1 before deleting $file_path_2:" | _filter_scratch`; line 43: `$XFS_IO_PROG -c "fiemap -v" $file_path_1 | _filter_fiemap_flags`; line 45: `rm -f $file_path_2`; line 47: `echo "Fiemap of $file_path_1 after deleting $file_path_2:" | _filter_scratch`; line 52: `_scratch_mkfs >> $seqres.full 2>&1`; line 53: `_scratch_mount`. It documents fixed kernel commit context at line 25: `_fixed_by_kernel_commit 4fc7b5722824 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick subvol fiemap clone`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 279 | Create subvolume 'SCRATCH_MNT/subv1' | Create subvolume 'SCRATCH_MNT/subv2' |  | Testing with same subvolume and without transaction commit |  | wrote 65536/65536 bytes at offset 0 | XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec) | ... (39 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
