# sources/test-tools/xfstests/tests/btrfs/252

## Purpose
Test that send and balance can run in parallel, without failures and producing correct results. Before kernel 5.3 it was possible to run both operations in parallel, however it was buggy and caused sporadic failures due to races, so it was disabled in kernel 5.3 by commit 9e967495e0e0ae ("Btrfs: prevent send failures and crashes due to concurrent relocation"). There is a now a patch that enables both operations to safely run in parallel, and it has the following subject: "btrfs: make send work with concurrent block group relocation" This also serves the purpose of testing a succession of incremental send. In this subset it primarily covers Btrfs send/receive stream generation and replay.

## Important APIs, Types, and Functions
The fstest declaration is `auto send balance stress`. Requirement and capability gates: line 44: `_require_scratch_size $(($LOAD_FACTOR * 6 * 1024 * 1024))`; line 45: `_require_fssum`. Local helper surface: `_cleanup()` (line 25), `balance_loop()` (line 47). Important command/API calls include line 23: `_begin_fstest auto send balance stress`; line 28: `if [ ! -z $balance_pid ]; then`; line 29: `kill $balance_pid &> /dev/null`; line 30: `wait $balance_pid`; line 47: `balance_loop()`; line 52: `_run_btrfs_balance_start $SCRATCH_MNT > /dev/null`; line 57: `_scratch_mkfs >> $seqres.full 2>&1`; line 58: `_scratch_mount`; line 60: `num_snapshots=$((10 + $LOAD_FACTOR * 2))`; line 61: `avg_ops_per_snapshot=$((1000 * LOAD_FACTOR))`; line 62: `total_fsstress_ops=$((num_snapshots * avg_ops_per_snapshot))`; line 65: `snapshots_dir="$SCRATCH_MNT/snapshots"`; line 66: `dest_dir="$SCRATCH_MNT/received"`; line 69: `mkdir -p "$snapshots_dir"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto send balance stress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, creates or deletes subvolumes/snapshots, generates and replays send streams, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. It persists send streams, fssum files, or received subvolumes in a temporary test directory and validates replay on a freshly formatted scratch filesystem. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, fssum, fsstress. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 252 | Silence is golden`.

## Risks and Edge Cases
send-stream ordering bugs can emit invalid paths, clone sources, link records, or parent references that only appear after replaying onto a clean filesystem. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
