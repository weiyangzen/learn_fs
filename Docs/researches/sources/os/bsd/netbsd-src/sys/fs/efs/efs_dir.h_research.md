# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_dir.h

Read completely: 185 lines.

Defines the EFS directory block and directory entry layout. A directory block is 512 bytes with magic `0xbeef`, a first-used offset, a slot count, and a shared `db_space` area containing compacted entry offsets, free space, and variable-length entries.

Directory entry offsets are stored right-shifted by one because entries are even-aligned. `EFS_DIRENT_OFF_EXPND`, `EFS_DIRENT_OFF_COMPT`, and `EFS_DIRENT_OFF_VALID` handle this encoding. Slot zero means free.

`struct efs_dirent` stores a big-endian inode number plus an unterminated variable-length name. `EFS_DIRENT_SIZE()` computes the padded entry size needed for 16-bit alignment. The extensive comments explain insertion/removal/free-space behavior and IRIX compatibility assumptions.
