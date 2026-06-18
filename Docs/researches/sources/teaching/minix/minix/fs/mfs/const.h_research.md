# File Research: sources/teaching/minix/minix/fs/mfs/const.h

`const.h` collects MFS layout constants, table sizes, operation codes, and derived size macros. It defines V2/V3 inode zone layout values (`V2_NR_DZONES`, `V2_NR_TZONES`), the in-core inode table size (`NR_INODES`), and the inode hash size/mask used by `inode.c`.

Filesystem identity constants include legacy and V3 superblock magic values, but this MFS implementation only accepts `SUPER_V3` in `read_super`. Directory operations use `LOOK_UP`, `ENTER`, `DELETE`, and `IS_EMPTY`, all consumed by `search_dir`. `WMAP_FREE` controls freeing behavior in `write_map`.

The file also defines inode dirty/time-update flags (`IN_CLEAN`, `IN_DIRTY`, `ATIME`, `CTIME`, `MTIME`), root and layout block numbers (`ROOT_INODE`, `BOOT_BLOCK`, `SUPER_BLOCK_BYTES`, `START_BLOCK`), directory entry sizing, bitmap geometry helpers, and V2 disk inode/indirect sizing macros.
