# sources/test-tools/xfstests/tests/btrfs/199

## Purpose

`sources/test-tools/xfstests/tests/btrfs/199` is btrfs fstests case `199`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test if btrfs discard mount option is trimming adjacent extents across block groups boundary. The test case uses loopback device and file used space to detect trimmed bytes. There is a long existing bug that btrfs doesn't discard all space for above mentioned case. We need less than 2G data write, consider it 2G and double it just in case The margin when checking trimmed size. The margin is for tree blocks, calculated by 3 * max_tree_block_size

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick trim fiemap` declares tags `auto quick trim fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_loop`, `_require_xfs_io_command "fiemap"`, `_require_scratch_size	$((4 * 1024 * 1024))`, `_notrun "Non-continuous extent bytenr detected"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `umount $loop_mnt &> /dev/null`; `_destroy_loop_device $loop_dev &> /dev/null`; `rm -rf $tmp.*`; `_require_loop`; `_require_scratch_size	$((4 * 1024 * 1024))`; `loop_file="$SCRATCH_MNT/image"`; `_scratch_mount`; `truncate -s 10G "$loop_file"`; `_mkfs_dev -d SINGLE "$loop_file"`; `loop_dev=$(_create_loop_device "$loop_file")`; `loop_mnt=$tmp/loop_mnt`; `size1_kb=$(du $loop_file| cut -f1)`; `rm -f $loop_mnt/cross_boundary`; `size2_kb=$(du $loop_file | cut -f1)`; `echo "loopback file size before discard: $size1_kb KiB" >> $seqres.full`; `echo "loopback file size after discard:  $size2_kb KiB" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick trim fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
