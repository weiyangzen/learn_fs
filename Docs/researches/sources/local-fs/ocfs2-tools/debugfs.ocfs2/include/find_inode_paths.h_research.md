# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_inode_paths.h

## Role

This header declares the inode-to-path lookup function used by `locate`, `ncheck`, and `findpath`.

## API

`find_inode_paths(ocfs2_filesys *fs, char **args, int findall, uint32_t count, uint64_t *blkno, FILE *out)` traverses directories looking for names pointing at the requested inode block numbers.

## Implementation

The function is implemented in `find_inode_paths.c`.
