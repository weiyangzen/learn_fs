# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_inode_paths.c

## Role

`find_inode_paths.c` implements pathname reconstruction for `locate`, `ncheck`, and `findpath`.

## Algorithm

It recursively walks directory entries from the filesystem root, builds path strings up to 4096 bytes, skips `.` and `..`, compares each entry’s inode against the requested inode list, and prints matches through `dump_inode_path()`.

`findall` controls whether traversal stops after one path per requested inode or continues to find all visible paths.

## Dependencies

It uses libocfs2 directory iteration, OCFS2 file-type values, and shared debugfs output/error helpers.

## Risk Areas

The search is a directory-tree traversal, so it can be expensive and can miss unreachable/orphaned inodes. It has a hard path length guard and aborts traversal on allocation or path-length failure.
