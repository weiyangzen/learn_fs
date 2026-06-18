# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.c

Implements read-side ext4 extent lookup helpers. Static binary searches find the applicable index entry at internal levels or extent entry at leaf level. `ext4_ext_in_cache` checks the inode extent cache and materializes a cached extent; `ext4_ext_put_cache` stores an extent start/logical range/type in the inode cache.

`ext4_ext_find_extent` starts from the inode-embedded extent header, validates magic, descends through index blocks with `bread`, releases previous path buffers while descending, and returns a path whose `ep_ext` points at the selected leaf extent. It returns `NULL` on bad magic or read failure. No extent mutation or allocation is implemented here.
