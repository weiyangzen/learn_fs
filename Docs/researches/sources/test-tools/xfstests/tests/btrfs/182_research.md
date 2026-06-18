# sources/test-tools/xfstests/tests/btrfs/182

## Purpose

`sources/test-tools/xfstests/tests/btrfs/182` is btrfs fstests case `182`. It targets balance relocation behavior. Source comments describe the scenario as: Test if balance will report false ENOSPC error This is a long existing bug, caused by over-estimated metadata space_info::bytes_may_use. There is one proposed patch for btrfs-progs to fix it, titled: "btrfs-progs: balance: Sync the fs before balancing metadata chunks" Create some small files to take up enough metadata reserved space

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick balance` declares tags `auto quick balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/subvol" > /dev/null`; `_pwrite_byte 0xcd 0 1K "$SCRATCH_MNT/subvol/file_$i" > /dev/null`; `_run_btrfs_balance_start -m $SCRATCH_MNT >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
