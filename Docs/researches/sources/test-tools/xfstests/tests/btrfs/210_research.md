# sources/test-tools/xfstests/tests/btrfs/210

## Purpose

`sources/test-tools/xfstests/tests/btrfs/210` is btrfs fstests case `210`. It targets subvolume/snapshot metadata, quota-group accounting and limits. Source comments describe the scenario as: Test that a new snapshot created with qgroup inherit passed should mark qgroup numbers inconsistent. Sync the fs to ensure data written to disk so that they can be accounted by qgroup Create a snapshot with qgroup inherit If qgroup is not marked inconsistent automatically, btrfs check would report error.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup snapshot` declares tags `auto quick qgroup snapshot`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/src" > /dev/null`; `_pwrite_byte 0xcd 0 16M "$SCRATCH_MNT/src/file" > /dev/null`; `sync`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT"`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup create 1/0 "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG subvolume snapshot -i 1/0 "$SCRATCH_MNT/src" \`; `"$SCRATCH_MNT/snapshot" > /dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup snapshot` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
