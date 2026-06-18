# sources/test-tools/xfstests/tests/btrfs/167

## Purpose

`sources/test-tools/xfstests/tests/btrfs/167` is btrfs fstests case `167`. It targets multi-device or RAID volume behavior, compression interactions. Source comments describe the scenario as: Test if btrfs will corrupt compressed data extent without data csum by replacing it with uncompressed data, when doing device replace. This could be fixed by the following kernel commit: ac0b4145d662 ("btrfs: scrub: Don't use inode pages for device replace") Create nodatasum inode Write the compressed data back to disk Replace the device Unmount to drop all cache so next read will read from disk Now the EXTENT_DATA item still marks the extent as compressed, but the on-disk data is uncompressed, thus reading it as compressed

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick replace volume remount compress` declares tags `auto quick replace volume remount compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 2`, `_require_scratch_dev_pool_equal_size`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_scratch_dev_pool_equal_size`; `_scratch_dev_pool_get 1`; `_scratch_pool_mkfs >> $seqres.full 2>&1`; `_scratch_mount "-o nodatasum"`; `touch $SCRATCH_MNT/nodatasum_file`; `_scratch_remount "datasum,compress"`; `_pwrite_byte 0xcd 0 128K $SCRATCH_MNT/nodatasum_file > /dev/null`; `sync`; `_btrfs replace start -Bf 1 $SPARE_DEV $SCRATCH_MNT`; `_scratch_unmount`; `_mount $SPARE_DEV $SCRATCH_MNT`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick replace volume remount compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
