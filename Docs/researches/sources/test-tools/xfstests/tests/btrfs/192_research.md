# sources/test-tools/xfstests/tests/btrfs/192

## Purpose

`sources/test-tools/xfstests/tests/btrfs/192` is btrfs fstests case `192`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test btrfs consistency after each FUA for a workload with snapshot creation and removal cap nr_cpus to 8 to avoid spending too much time on hosts with many cpus Discard the whole devices so when some tree pointer is wrong, it won't point to some older valid tree blocks, so we can detect it. Use no-holes to avoid warnings of missing file extent items (expected for holes due to mix of buffered and direct IO writes). And use 4K nodesize to bump tree height. Do something small to make snapshots different Replay and check each fua/flush (specified by $2) point.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto replay snapshot stress recoveryloop` declares tags `auto replay snapshot stress recoveryloop`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/attr`, `./common/dmlogwrites`; requirements: `_require_command "$BLKDISCARD_PROG" blkdiscard`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_log_writes`, `_require_scratch`, `_require_attrs`, `_require_btrfs_support_sectorsize 4096`; local shell helpers: `_cleanup()`, `snapshot_workload()`, `delete_workload()`, `log_writes_fast_replay_check()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_btrfs_fs_feature "no_holes"`; `_require_btrfs_mkfs_feature "no-holes"`; `_require_scratch`; `_require_attrs`; `_log_writes_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/src > /dev/null`; `mkdir -p $SCRATCH_MNT/snapshots`; `snapshot_workload()`; `$BTRFS_UTIL_PROG subvolume snapshot \`; `$SCRATCH_MNT/src $SCRATCH_MNT/snapshots/$i \`; `touch "$SCRATCH_MNT/src/padding/$i"`; `$SETFATTR_PROG -n 'user.x1' -v $xattr_value "$SCRATCH_MNT/src/padding/$i"`; `snapshot_workload &`; `_log_writes_unmount`; `log_writes_fast_replay_check fua "$SCRATCH_DEV"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto replay snapshot stress recoveryloop` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
