# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/e2image.h

Defines `struct ext2_image_hdr`, the on-disk/header format for e2image output.

Fields capture:
- Magic number and descriptor string.
- Source filesystem host/network/device identity.
- Filesystem UUID and block size.
- Image file device, inode, and creation time low/high words.
- Offsets to superblock/descriptors, inode table data, inode bitmap data, and block bitmap data.
- Reserved fields for future extension.

Implementation notes:
- The comment notes this format uses POSIX IO interfaces unlike most libext2fs code.
- The header contains only the structure definition and no functions.
