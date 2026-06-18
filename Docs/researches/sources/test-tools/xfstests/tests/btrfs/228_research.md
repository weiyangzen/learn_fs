# sources/test-tools/xfstests/tests/btrfs/228

## Purpose
Test correct operation of free objectid related functionality create a new subvolume to validate its objectid is initialized accordingly, the expected value is 256 as this is the first free objectid in a new file system Subvolume creation used to commit the transaction used to create it, but after the patch "btrfs: don't commit transaction for every subvol create", that changed, so sync the fs to commit any open transaction. create new file in the new subvolume to validate its objectid is set as expected. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick volume`. Requirement and capability gates: line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 14: `_require_scratch`; line 15: `_require_btrfs_command inspect-internal dump-tree`; line 17: `_scratch_mkfs > /dev/null`; line 18: `_scratch_mount`; line 23: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/newvol >> $seqres.full 2>&1 || _fail "couldn't create subvol"`; line 29: `$BTRFS_UTIL_PROG filesystem sync $SCRATCH_MNT`; line 31: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t1 $SCRATCH_DEV | grep -q "256 ROOT_ITEM" || _fail "First subvol with id 256 doesn't exist"`; line 36: `touch $SCRATCH_MNT/newvol/file1 || _fail "Cannot create file in new subvol"`; line 39: `sync`; line 43: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t5 $SCRATCH_DEV | grep -A2 "256 DIR_ITEM 1903355334" > $output_file`; line 54: `$BTRFS_UTIL_PROG inspect-internal dump-tree -t256 $SCRATCH_DEV > $output_file`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick volume`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 228 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
