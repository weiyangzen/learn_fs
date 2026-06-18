# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/res_gdt.c

Supports reserved group descriptor table blocks for online resizing. `ext2fs_list_backups()` enumerates backup-super/GDT groups for sparse_super, sparse_super2, and non-sparse filesystems.

`ext2fs_create_resize_inode()` creates or repairs the resize inode’s double-indirect mapping so reserved primary and backup GDT blocks are represented. It allocates the double-indirect block if missing, verifies expected primary/backup GDT block locations, writes dirty indirect blocks, updates inode size/block counts, and writes the resize inode.

The code explicitly does not handle extents for this inode and relies on reserved blocks already being marked in-use during filesystem initialization.
