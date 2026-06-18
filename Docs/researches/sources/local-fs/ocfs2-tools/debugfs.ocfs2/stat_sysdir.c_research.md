# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/stat_sysdir.c

## Role

`stat_sysdir.c` implements `stat_sysdir`, a full dump of the OCFS2 superblock and system directory objects.

## Behavior

It prints the current device, dumps the superblock and superblock inode, verifies the system directory, then iterates entries under `//`. For each system object except `..`, it reads the inode, prints metadata, traverses associated extents/chains/local alloc/truncate logs as appropriate, and lists child entries for system directories.

If the object is the slot map system file, it reads and dumps either the extended or classic slot map.

## Dependencies

It reuses directory iteration, inode dumping, chain/extent traversal, slot-map reading, and the global reusable block buffer.

## Risk Areas

The function performs broad metadata traversal and can generate large output. It assumes system-directory entries are readable and formatted enough for the shared dump routines.
