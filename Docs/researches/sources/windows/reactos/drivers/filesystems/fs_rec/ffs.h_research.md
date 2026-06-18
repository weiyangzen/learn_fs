# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ffs.h

Packed BSD FFS/UFS on-disk structure definitions for recognition. The header imports a large FreeBSD-compatible `fs` superblock layout as `FFSD_SUPER_BLOCK`, including legacy UFS fields, cylinder-group summary data, mount and volume names, snapshot fields, size/address fields, flags, maximum file size, masks, and final `fs_magic`. It also defines a packed BSD `disklabel` as `FFSD_DISKLABEL`, including geometry, boot names, checksums, and an array of partition entries with filesystem type and UFS fragment/cylinder metadata.

Recognition constants define UFS1 and UFS2 superblock offsets (`8192` and `65536`), superblock read size `8192`, UFS magic values, disklabel magic, label sector, maximum partitions, and the `FS_BSDFFS` partition type. Compile-time assertions pin selected superblock offsets such as `fs_cgsize`, `fs_fmod`, and `fs_ocsp`, protecting the recognizer's use of native on-disk layouts.
