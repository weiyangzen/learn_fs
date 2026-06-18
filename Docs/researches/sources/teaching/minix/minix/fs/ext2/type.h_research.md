# File Research: sources/teaching/minix/minix/fs/ext2/type.h

This header defines disk-format ext2 inode, directory entry descriptor, directory traversal macros, and runtime options.

Types:
- `d_inode`: disk inode format, matching ext2 fields and OS-dependent sections.
- `struct ext2_disk_dir_desc`: ext2 directory record header plus first name byte.
- `struct opt`: server options for Orlov allocation, MFS-like allocation, reserved block usage, alternate superblock, and preallocation.

Macros:
- `CUR_DISC_DIR_POS`, `NEXT_DISC_DIR_DESC`, `NEXT_DISC_DIR_POS` for directory block traversal.

Role:
- Provides disk-level structure definitions used by inode copy, directory lookup/getdents, symlink fast storage sizing, and mount option parsing.

Notable detail:
- The directory entry structure models revision >= 0.5 file type layout where high name length bits became `d_file_type`.
