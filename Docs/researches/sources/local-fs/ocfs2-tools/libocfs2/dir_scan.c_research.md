# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_scan.c

Sequential directory scan API.

`ocfs2_open_dir_scan()` validates the target directory, allocates a scan object and one block buffer, reads the directory as a cached inode, computes total blocks from inode size, and returns an opaque `ocfs2_dir_scan`.

`ocfs2_get_next_dir_entry()` refills the buffer with `get_more_dir_blocks()` as needed using `ocfs2_extent_map_get_blocks()` and `ocfs2_read_dir_block()`. It validates each dirent, skips empty entries, dot entries when requested, and directory trailers, then copies the next valid dirent to caller storage. End of iteration is signaled by returning success with a zeroed dirent.

`ocfs2_close_dir_scan()` frees the cached inode, buffer, and scan object. Debug mode prints all names in a selected directory.
