# sources/test-tools/xfstests/tests/btrfs/173

## Purpose

`sources/test-tools/xfstests/tests/btrfs/173` is btrfs fstests case `173`. It targets compression interactions. Source comments describe the scenario as: Test swap file activation restrictions specific to Btrfs, swap file can't be CoW file nor compressed file. We can't use _format_swapfile because we don't want chattr +C, and we can't unset it after the swap file has been created. Make sure we have a COW file if we were mounted with "-o nodatacow".

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap compress` declares tags `auto quick swap compress`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`, `_require_chattr C`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `_scratch_mkfs >> $seqres.full 2>&1`; `_scratch_mount`; `rm -f "$SCRATCH_MNT/swap"`; `touch "$SCRATCH_MNT/swap"`; `if _normalize_mount_options "$MOUNT_OPTIONS" | grep -q "nodatacow"; then`; `_require_chattr C`; `chmod 0600 "$SCRATCH_MNT/swap"`; `_pwrite_byte 0x61 0 $(($(_get_page_size) * 10)) "$SCRATCH_MNT/swap" >> $seqres.full`; `swapon "$SCRATCH_MNT/swap" 2>&1 | _filter_scratch`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
