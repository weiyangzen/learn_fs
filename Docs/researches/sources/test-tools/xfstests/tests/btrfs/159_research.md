# sources/test-tools/xfstests/tests/btrfs/159

## Purpose

`sources/test-tools/xfstests/tests/btrfs/159` is btrfs fstests case `159`. It targets log-tree replay and fsync crash recovery. Source comments describe the scenario as: Test that when we have the no-holes mode enabled and a specific metadata layout, if we punch a hole and fsync the file, at replay time the whole hole was preserved. We create the filesystem with a node size of 64Kb because we need to create a specific metadata layout in order to trigger the bug we are testing. At the moment the node size can not be smaller then the system's page size, so given that the largest possible page size is 64Kb and by default the node size is set to the system's page size value, we explicitly create a filesystem with a 64Kb node size. Create our test file with 832 extents of 256Kb each. Before each

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick punch log` declares tags `auto quick punch log`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmflakey`; requirements: `_require_scratch`, `_require_dm_target flakey`, `_require_xfs_io_command "fpunch"`, `_require_odirect`, `_require_metadata_journaling $SCRATCH_DEV`; local shell helpers: `_cleanup()`, `run_test()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_cleanup_flakey`; `rm -f $tmp.*`; `_require_scratch`; `_require_dm_target flakey`; `_scratch_mkfs -O no-holes -n $((64 * 1024)) >>$seqres.full 2>&1`; `_init_flakey`; `_scratch_mount`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab -b 256K $offset 256K" \`; `sync`; `$XFS_IO_PROG -c "fpunch $((punch_offset + 128 * 1024 - 4000)) 256K" \`; `-c "fsync" \`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_flakey_drop_and_remount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick punch log` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
