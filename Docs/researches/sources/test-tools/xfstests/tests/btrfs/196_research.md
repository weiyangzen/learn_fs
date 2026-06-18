# sources/test-tools/xfstests/tests/btrfs/196

## Purpose

`sources/test-tools/xfstests/tests/btrfs/196` is btrfs fstests case `196`. It targets log-tree replay and fsync crash recovery, multi-device or RAID volume behavior. Source comments describe the scenario as: Test multi subvolume fsync to test a bug where we'd end up pointing at a block we haven't written.  This was fixed by the patch btrfs: fix incorrect updating of log root tree Will do log replay and check the filesystem. Use thin device as replay device, which requires $SCRATCH_DEV and we need extra device as log device Use a thin device to provide deterministic discard behavior. Discards are used by the log replay tool for fast zeroing to prevent out-of-order replay issues. First create all the subvolumes We need to mount the fs because btrfsck won't bother checking the log.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto metadata log volume` declares tags `auto metadata log volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmthin`, `./common/dmlogwrites`; requirements: `_require_scratch_nocheck`, `_require_log_writes`, `_require_dm_target thin-pool`, `_require_fio $fio_config`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch_nocheck`; `fallocate=none`; `fsync=1`; `echo "filename=$SCRATCH_MNT/$i/file" >> $fio_config`; `_log_writes_mkfs >> $seqres.full 2>&1`; `_log_writes_mark mkfs`; `_log_writes_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/$i" > /dev/null`; `_log_writes_unmount`; `prev=$(_log_writes_mark_to_entry_number mkfs)`; `[ -z "$prev" ] && _fail "failed to locate entry mark 'mkfs'"`; `_dmthin_mount`; `_dmthin_check_fs`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto metadata log volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
