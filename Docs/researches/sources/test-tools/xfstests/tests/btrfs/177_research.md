# sources/test-tools/xfstests/tests/btrfs/177

## Purpose

`sources/test-tools/xfstests/tests/btrfs/177` is btrfs fstests case `177`. It targets balance relocation behavior. Source comments describe the scenario as: Test relocation (balance and resize) with an active swap file. Eliminate the differences between the old and new output formats Old format: Resize 'SCRATCH_MNT' of '1073741824' New format: Resize device id 1 (SCRATCH_DEV) from 3.00GiB to 1.00GiB Convert both outputs to: Resized to 1073741824 remove trailing zeroes get the first unit char, for example return G in case we have GiB

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick swap balance` declares tags `auto quick swap balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_swapfile`, `_require_scratch_size $((3 * 1024 * 1024)) #kB`; local shell helpers: `convert_resize_output()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_swapfile`; `convert_resize_output()`; `swapfile="$SCRATCH_MNT/swap"`; `_require_scratch_size $((3 * 1024 * 1024)) #kB`; `_scratch_mkfs_sized $fssize >> $seqres.full 2>&1`; `_scratch_mount`; `dd if=/dev/zero of="$SCRATCH_MNT/fill" bs=4096 count=1 >> $seqres.full 2>&1`; `_run_btrfs_balance_start "$SCRATCH_MNT" >>$seqres.full`; `dd if=/dev/zero of="$SCRATCH_MNT/refill" bs=4096 >> $seqres.full 2>&1`; `$BTRFS_UTIL_PROG filesystem resize $((3 * fssize)) "$SCRATCH_MNT" | convert_resize_output`; `rm -f "$SCRATCH_MNT/fill"`; `rm -f "$SCRATCH_MNT/refill"`; `$BTRFS_UTIL_PROG filesystem resize 1G "$SCRATCH_MNT" 2>&1 | grep -o "Text file busy"`; `$BTRFS_UTIL_PROG filesystem resize $fssize "$SCRATCH_MNT" | convert_resize_output`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick swap balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
