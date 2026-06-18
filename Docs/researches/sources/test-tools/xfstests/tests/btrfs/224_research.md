# sources/test-tools/xfstests/tests/btrfs/224

## Purpose
Test the assign functionality of qgroups Test assign qgroup for submodule with shared extents by reflink Test assign qgroup for submodule without shared extents Test snapshot with assigning qgroup for higher level qgroup success, all done. In this subset it primarily covers quota group accounting, assignment, limits, and rescan behavior, reflink/clone extent sharing, subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick qgroup`. Requirement and capability gates: line 16: `_require_scratch`; line 17: `_require_btrfs_qgroup_report`; line 18: `_require_cp_reflink`. Local helper surface: `assign_shared_test()` (line 21), `assign_no_shared_test()` (line 45), `snapshot_test()` (line 66). Important command/API calls include line 10: `_begin_fstest auto quick qgroup`; line 13: `. ./common/reflink`; line 17: `_require_btrfs_qgroup_report`; line 18: `_require_cp_reflink`; line 23: `_scratch_mkfs > /dev/null 2>&1`; line 24: `_scratch_mount`; line 26: `echo "=== qgroup assign shared test ===" >> $seqres.full`; line 27: `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT`; line 28: `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; line 30: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/a >> $seqres.full`; line 31: `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/b >> $seqres.full`; line 34: `_cp_reflink "$SCRATCH_MNT"/a/file1 "$SCRATCH_MNT"/b/file1`; line 36: `$BTRFS_UTIL_PROG qgroup create 1/100 $SCRATCH_MNT`; line 37: `$BTRFS_UTIL_PROG qgroup assign $SCRATCH_MNT/a 1/100 $SCRATCH_MNT`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick qgroup`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, enables and inspects quota groups, runs btrfs check or xfstests scratch checks, cycles mounts to force persistence. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Quota state persists in qgroup metadata and is forced through rescans, syncs, commits, and filesystem checks. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 224 | Silence is golden`.

## Risks and Edge Cases
qgroup tests are sensitive to delayed accounting, rescan completion, shared extents, and limit enforcement after transaction commits. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
