# sources/test-tools/xfstests/tests/btrfs/174

## Purpose

`sources/test-tools/xfstests/tests/btrfs/174` is btrfs fstests case `174`. It targets compression interactions. Source comments describe the scenario as: Test restrictions on operations that can be done on an active swap file specific to Btrfs. Turning off nocow doesn't do anything because the file is not empty, not because the file is a swap file, but make sure this works anyways. Compression we reject outright. We pass the -c (compress) flag to force defrag even if the file isn't fragmented.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap compress` declares tags `auto quick swap compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/swapvol" >> $seqres.full`; `swapfile="$SCRATCH_MNT/swapvol/swap"`; `$LSATTR_PROG -l "$swapfile" | _filter_scratch | _filter_spaces`; `$BTRFS_UTIL_PROG subvolume snapshot "$SCRATCH_MNT/swapvol" \`; `$BTRFS_UTIL_PROG filesystem defrag -c "$swapfile" 2>&1 | grep -o "Text file busy"`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
