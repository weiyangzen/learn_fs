# sources/test-tools/xfstests/tests/btrfs/247

## Purpose
Tests rename/exchange behavior when subvolumes are involved. Rename/exchanges across subvolumes are forbidden. This is also a regression test for 3f79f6f6247c ("btrfs: prevent rename2 from exchanging a subvol with a directory from different parents"). Create 2 subvols to use as parents for the rename ops Ensure cross subvol ops are forbidden Prepare a subvolume and a directory whose parents are different subvolumes Ensure exchanging a subvol with a dir when both parents are different fails Test also ordinary renames. In this subset it primarily covers multi-device, RAID, seed/sprout, or device-management paths, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick rename subvol`. Requirement and capability gates: line 17: `_require_renameat2 exchange`; line 18: `_require_scratch`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 17: `_require_renameat2 exchange`; line 18: `_require_scratch`; line 20: `_scratch_mkfs >> $seqres.full 2>&1`; line 21: `_scratch_mount`; line 24: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 1>/dev/null`; line 25: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 1>/dev/null`; line 31: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1/sub-subvol 1>/dev/null`; line 32: `mkdir $SCRATCH_MNT/subvol2/dir`; line 41: `echo "subvolumes rename"`; line 51: `mv $SCRATCH_MNT/subvol2/ $SCRATCH_MNT/subvol2.`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick rename subvol`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 247 | cross-subvol none/none -> No such file or directory | cross-subvol none/regu -> No such file or directory | cross-subvol none/symb -> No such file or directory | cross-subvol none/dire -> No such file or directory | cross-subvol none/tree -> No such file or directory | cross-subvol regu/none -> No such file or directory | cross-subvol regu/regu -> Invalid cross-device link | ... (54 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
