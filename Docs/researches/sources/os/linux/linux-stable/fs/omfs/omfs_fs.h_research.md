# File Research: sources/os/linux/linux-stable/fs/omfs/omfs_fs.h

## Scope

This header defines OMFS on-disk constants and packed-style disk structures used by the Linux OMFS driver.

## Constants

- Magic/type values: `OMFS_MAGIC`, `OMFS_IMAGIC`, `OMFS_DIR`, `OMFS_FILE`, inode type letters for normal/continuation/system.
- Layout limits and offsets: name length 256, directory table start `0x1b8`, first extent table start `0x1d0`, continuation extent start `0x40`, XOR header count 19, max block size 8192, max cluster size 8, max blocks `1 << 31`.

## On-Disk Structures

- `omfs_super_block` stores root block pointer, total blocks, magic, block size, mirror count, and system-block size.
- `omfs_header` is the common block header with self pointer, body size, CRC, version, type, magic, and XOR checksum.
- `omfs_root_block` stores global filesystem metadata: total blocks, root directory, bitmap location, block size, cluster size, mirrors, and volume label.
- `omfs_inode` stores common header, parent/sibling links, millisecond ctime, file type, filename, and byte size.
- `omfs_extent_entry` stores cluster start and block count.
- `omfs_extent` stores next extent-table block, extent count, filler, and flexible extent entries.

## Dependencies And Risks

- Fields are big-endian and require explicit conversion in implementation files.
- The structures are used as direct overlays on buffer-head data, so layout offsets in this header are part of the on-disk ABI.
