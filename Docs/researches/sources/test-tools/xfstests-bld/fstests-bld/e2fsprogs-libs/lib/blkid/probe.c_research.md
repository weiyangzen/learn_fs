# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.c

## Purpose
`probe.c` is the legacy libblkid content scanner. It verifies cached device entries by opening the block device, reading known superblock offsets, matching a static magic table, and extracting tags such as `TYPE`, `LABEL`, `UUID`, `SEC_TYPE`, `EXT_JOURNAL`, and `MOUNT`.

## Important APIs, Types, and Functions
The externally visible APIs are `blkid_verify()` and `blkid_known_fstype()`, plus a `TEST_PROGRAM` main. Core helpers include `get_buffer()`, `check_mdraid()`, `set_uuid()`, `get_ext2_info()`, filesystem support probes for ext2/3/4/ext4dev/JBD, FAT, NTFS, XFS, Reiser, JFS, UDF/ISO, OCFS, GFS/GFS2, HFS/HFS+, LVM2, Btrfs, LUKS, swap, and small label conversion/checksum helpers.

## Control Flow
`blkid_verify()` first uses cache age, device mtime, and previous verification flags to avoid unnecessary probes. If probing is required, it tries mdraid and then walks `type_array`, reads the 1 KiB window containing each magic string through `get_buffer()`, calls the optional filesystem-specific probe, and updates tags on the `blkid_dev` when a match succeeds. If a cached type fails, it clears all tags and retries a full scan.

## State, Persistence, Dependencies, Risks, and Test Signals
State is held in `blkid_dev` tags and timestamps, cache changed flags, probe buffers, and static Linux filesystem-support caches. Persistence is indirect through `save.c` once cache flags are changed. Dependencies include `blkidP.h`, `probe.h`, libuuid, endian helpers, `/proc/filesystems`, `/lib/modules`, Linux io, and on-disk structure layouts. Risks include stale kernel support detection, trusting packed on-disk fields, partial reads around large offsets, native-endian swap handling, and subtle type ordering in `type_array`. Test signals include the `tst_probe` image corpus, cache revalidation behavior, ext feature discrimination, FAT/NTFS label extraction, LVM2 CRC rejection, and mdraid end-of-device probing.
