# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_sb.h

Read completely: 70 lines.

Defines the 92-byte EFS superblock. Fields include filesystem size, first cylinder group, cylinder group size, inode blocks per group, geometry, cylinder group count, dirty flag, timestamp, magic, volume names, bitmap size/free counts, bitmap block for grown filesystems, replicated superblock block, last inode, spare bytes, and checksum.

Defines original and grown-filesystem magic values (`EFS_SB_MAGIC`, `EFS_SB_NEWMAGIC`), checksum size excluding the checksum field, and the clean dirty-flag value.

The comments capture IRIX-version nuances, including grown filesystems, replicated superblocks, and historical checksum variants.
