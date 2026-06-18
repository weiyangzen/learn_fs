# sources/test-tools/xfstests/tests/btrfs/138

## Purpose

`sources/test-tools/xfstests/tests/btrfs/138` is btrfs fstests case `138`. It targets compression interactions. Source comments describe the scenario as: Test decompression in the middle of large extents. Regression test for Linux kernel commit 6e78b3f7a193 ("Btrfs: fix btrfs_decompress_buf2page()"). Need 1GB for the uncompressed file plus <1GB for each compressed file. Checksum a piece in the middle of the file. This hits the unaligned case that caused the original bug. Create a large, uncompressed (but compressible) file. Copy the same data, but with compression enabled. The correct data is likely still cached. Cycle the mount to drop the cache and start fresh. Check the checksum.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto compress` declares tags `auto compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command property`, `_require_btrfs_no_nodatacow`, `_require_fs_space $SCRATCH_MNT $((1024 * 1024 * (1 + ${#algos[@]})))`; local shell helpers: `do_csum()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command property`; `_require_btrfs_no_nodatacow`; `algos=($(_btrfs_compression_algos))`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `dd if="$1" bs=4K skip=555 count=100 2>>$seqres.full| md5sum | cut -d ' ' -f 1`; `touch "${SCRATCH_MNT}/uncompressed"`; `$BTRFS_UTIL_PROG property set "${SCRATCH_MNT}/uncompressed" compression ""`; `_ddt of="${SCRATCH_MNT}/uncompressed" bs=1M count=1K 2>&1 | _filter_dd`; `csum="$(do_csum "${SCRATCH_MNT}/uncompressed")"`; `touch "${SCRATCH_MNT}/${algo}"`; `$BTRFS_UTIL_PROG property set "${SCRATCH_MNT}/${algo}" compression "${algo}"`; `dd if="${SCRATCH_MNT}/uncompressed" of="${SCRATCH_MNT}/${algo}" bs=1M 2>&1 | _filter_dd`; `_scratch_cycle_mount`; `compressed_csum="$(do_csum "${SCRATCH_MNT}/${algo}")"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. Before/after checksums must match across remount, balance, or receive.
