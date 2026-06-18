# File Research: sources/os/linux/linux-stable/fs/bfs/Makefile

This Makefile builds the BFS filesystem module/object.

Build rules:
- `obj-$(CONFIG_BFS_FS) += bfs.o`
- `bfs-objs := inode.o file.o dir.o`

Integration:
- Controlled by `CONFIG_BFS_FS` from `Kconfig`.
- Links BFS superblock/inode, file, and directory operations into one `bfs` object.

Risk notes:
- No generated or optional components are present.
