# sources/test-tools/xfstests/tests/btrfs/136

## Purpose

`sources/test-tools/xfstests/tests/btrfs/136` is btrfs fstests case `136`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test btrfs-convert 1) create ext3 filesystem & populate it. 2) upgrade ext3 filesystem to ext4. 3) populate data. 4) source has combination of non-extent and extent files. 5) convert it to btrfs, mount and verify contents. ext4 does not support zoned block device Create & populate an ext3 filesystem mount and populate non-extent file Upgrade it to ext4.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto convert` declares tags `auto convert`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_nocheck`, `_require_non_zoned_device "${SCRATCH_DEV}"`, `_require_extra_fs ext3`, `_require_command "$BTRFS_CONVERT_PROG" btrfs-convert`, `_require_command "$MKFS_EXT4_PROG" mkfs.ext4`, `_require_command "$E2FSCK_PROG" e2fsck`, `_require_command "$TUNE2FS_PROG" tune2fs`, `_notrun "Could not create ext3 filesystem"`, `_notrun "block size $BLOCK_SIZE is not supported by ext3"`; local shell helpers: `populate_data()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_nocheck`; `_require_non_zoned_device "${SCRATCH_DEV}"`; `_require_command "$MKFS_EXT4_PROG" mkfs.ext4`; `mkdir -p $data_path`; `$MKFS_EXT4_PROG -F -t ext3 -b $BLOCK_SIZE $SCRATCH_DEV > $seqres.full 2>&1 || \`; `mount -t ext3 $SCRATCH_DEV $SCRATCH_MNT`; `_scratch_unmount`; `mount -t ext4 $SCRATCH_DEV $SCRATCH_MNT`; `_try_scratch_mount || _fail "Could not mount new btrfs fs"`; `btrfs_perm=\`md5sum "$BTRFS_MD5SUM" | cut -f1 -d' '\``; `ext_perm=\`md5sum "$EXT_MD5SUM" | cut -f1 -d' '\``; `echo "md5sum mismatch"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto convert` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. Before/after checksums must match across remount, balance, or receive.
