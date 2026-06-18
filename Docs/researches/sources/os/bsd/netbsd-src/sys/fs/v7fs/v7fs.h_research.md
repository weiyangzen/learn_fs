# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs.h

Read completely: 180 lines.

Defines the core on-disk layout and types for NetBSD’s Seventh Edition Unix filesystem support. The header documents the 512-byte boot block, superblock, inode-list area, and data block layout, with an 8 GB maximum volume size from 24-bit block addresses and about 1 GB maximum file size.

It defines V7-sized types for inode numbers, disk addresses, times, offsets, device numbers, and modes. Constants cover block size/shift, block rounding/truncation, boot/superblock/inode-list sectors, free-block and free-inode cache sizes, direct and indirect address indexes, directory name/path/link limits, root inode number, inode packing, and maximum inode calculations.

Structures include `v7fs_superblock`, `v7fs_freeblock`, `v7fs_dirent`, and `v7fs_inode_diskimage`, all packed to match disk format. The inode layout stores mode, nlink, uid/gid, file size, 40 bytes of encoded block addresses, and access/modify/change times. File type constants cover original V7 regular/directory/block/character files, obsolete multiplexed file types, and later BSD/NetBSD symlink/socket/fifo extensions.

Risks and notes: the address array comment notes 39 used bytes inside a 40-byte field for 13 three-byte addresses. `V7FS_RESIDUE_BSIZE(x)` assumes nonzero-style arithmetic and may be surprising for exact block boundaries. `V7FS_PATH_MAX` and `V7FS_LINK_MAX` defer to NetBSD limits because original V7 had no direct equivalents.
