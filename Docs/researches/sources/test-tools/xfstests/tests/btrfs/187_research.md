# sources/test-tools/xfstests/tests/btrfs/187

## Purpose

`sources/test-tools/xfstests/tests/btrfs/187` is btrfs fstests case `187`. It targets send/receive stream correctness, balance relocation behavior. Source comments describe the scenario as: Stress send running in parallel with balance and deduplication against files that belong to the snapshots used by send. The goal is to verify that these operations running in parallel do not lead to send crashing (trigger assertion failures and BUG_ONs), or send finding an inconsistent snapshot that leads to a failure (reported in dmesg/syslog). The test needs big trees (snapshots) with large differences between the parent and send snapshots in order to hit such issues with a good probability. We at least need 8GB of free space on $SCRATCH_DEV Ignore errors from dedupe. We just want to test for crashes and deadlocks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto send dedupe clone balance` declares tags `auto send dedupe clone balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/attr`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_dedupe`, `_require_attrs`, `_require_scratch_size $((8 * 1024 * 1024))`; local shell helpers: `dedupe_two_files()`, `dedupe_files_loop()`, `balance_loop()`, `full_send_loop()`, `inc_send_loop()`, `write_files_loop()`, `set_xattrs_loop()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dedupe`; `_require_attrs`; `_require_scratch_size $((8 * 1024 * 1024))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `dedupe_files_loop()`; `balance_loop()`; `_run_btrfs_balance_start -f -m $SCRATCH_MNT &> /dev/null`; `full_send_loop()`; `$BTRFS_UTIL_PROG send -f /dev/null \`; `inc_send_loop()`; `wait $full_send_pid`; `wait $inc_send_pid`; `kill $balance_pid`; `wait $balance_pid`; `_dmesg_since_test_start | grep -E -e '\bBTRFS error \(device .*?\):'`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto send dedupe clone balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
