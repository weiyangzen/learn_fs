# sources/sync-backup/casync/src/fssize.c

## Purpose

`fssize.c` detects the logical size of filesystem/image formats by reading known superblock/header layouts from an fd. It supports squashfs, Android boot images, FAT, and ext2/3/4.

## Important APIs, Types, and Functions

`read_file_system_size(int fd, uint64_t *ret)` reads a union large enough for the supported headers with `pread(fd, ..., 0)`. It returns negative errno on read failure, `0` when the image is too short or unrecognized, and `1` with `*ret` set when a supported format is recognized.

The local packed union contains FAT boot sector fields, squashfs superblock fields, Android boot image header fields, and an ext2/3/4 superblock located after a 1024-byte skip. FAT uses signature `0xaa55`; Android boot image magic is split across `_ANDROID_BOOTIMG_MAGIC_1` and `_ANDROID_BOOTIMG_MAGIC_2`.

## Control Flow

After a full header read, detection checks squashfs first, Android boot image second, FAT third, and ext2/3/4 last. Squashfs size is `bytes_used` aligned to 4096. Android size is a sum of page-aligned header, kernel, initrd, second stage, and dtb sizes when page size is a power of two. FAT size uses 16-bit sector count first, then 32-bit total sectors. Ext size multiplies block count by `1 << (10 + s_log_block_size)` if the shift is below 64.

## State and Persistence Behavior

The function is read-only and does not change file offset because it uses `pread()`. No process state is stored.

## Dependencies and Integration Points

It includes `fssize.h` and `util.h`, relying on endian typedefs/converters, `_packed_`, `ALIGN_TO`, `IS_POWER_OF_TWO`, and filesystem magic constants. It likely helps decide sparse/block image payload sizes during encode/decode.

## Risks and Edge Cases

There is a likely bug in `if (le32toh(superblock.squashfs.s_magic == SQUASHFS_MAGIC))`: the comparison is performed before endian conversion, so this does not actually convert the magic value. This may still work by accident on little-endian if the boolean result is passed through unchanged, but it is semantically wrong and can miss or mis-handle big-endian cases. The function requires reading the full union size, so valid shorter headers could be unrecognized. Android header size is hard-coded as 608. FAT signature alone is a weak signal without stronger validation.

## Test Signals

Tests should use synthetic images for each supported format, too-short files, unknown data, big-endian simulation or static analysis for the squashfs magic expression, invalid Android page sizes, FAT 16-bit versus 32-bit sector counts, ext block-size shifts near overflow, and fd offset preservation.
