# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/btrfs.h

Packed partial Btrfs superblock definition for the recognizer. It defines a 16-byte `BTRFS_UUID` and the early fields of `BTRFS_SUPER_BLOCK`: checksum, UUID, physical superblock address, flags, and magic. Compile-time offset assertions pin `uuid` at `0x20`, `sb_phys_addr` at `0x30`, and `magic` at `0x40`. Constants define the little-endian Btrfs magic value, primary superblock offset `0x10000`, and probe size `0x1000`.
