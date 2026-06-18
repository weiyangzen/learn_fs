# sources/test-tools/xfstests/tests/btrfs/183

## Purpose

`sources/test-tools/xfstests/tests/btrfs/183` is btrfs fstests case `183`. It targets compression interactions. Source comments describe the scenario as: Regression test for read corruption of compressed and shared extents after punching holes into a file. Create a file with 3 consecutive compressed extents, each corresponds to 128Kb of data (uncompressed size) and each is stored on disk as a 4Kb extent (compressed size, regardless of compression algorithm used). Each extent starts with 4Kb of zeroes, while the remaining bytes all have a value of 0xff. Clone the first extent into offsets 128K and 256K. Punch holes into the regions that are already full of zeroes.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone compress punch` declares tags `auto quick clone compress punch`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_reflink`, `_require_xfs_io_command "fpunch"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_reflink`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount "-o compress"`; `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 384K" \`; `-c "pwrite -S 0x00 0 4K" \`; `-c "pwrite -S 0x00 128K 4K" \`; `-c "pwrite -S 0x00 256K 4K" \`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foobar 0 128K 128K" \`; `-c "reflink $SCRATCH_MNT/foobar 0 256K 128K" \`; `echo "File digest after reflinking:"`; `$XFS_IO_PROG -c "fpunch 0 4K" \`; `echo 1 > /proc/sys/vm/drop_caches`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone compress punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
