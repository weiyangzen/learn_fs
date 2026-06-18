# File Research: sources/os/linux/linux/fs/jffs2/fs.c

This file provides Linux VFS superblock/inode integration for JFFS2: setattr, statfs, inode eviction/read/new-inode, remount, mount fill, GC inode fetch/release, and flash-type setup/cleanup.

`jffs2_do_setattr()` writes a new metadata inode node for mode/uid/gid/time/size changes. For device nodes and symlinks it preserves associated metadata data by re-encoding `dev_t` or reading the symlink target. Size extension is represented as a `JFFS2_COMPR_ZERO` hole node; truncate-to-zero uses deletion-priority allocation. After writing the new node, it updates VFS inode fields, truncates the fragment tree on shrink, adds hole nodes on extension, obsoletes old metadata, completes the flash reservation, and performs `truncate_setsize()` after dropping `f->sem`.

`jffs2_setattr()` runs VFS permission/preparation checks and updates POSIX ACL mode data after successful chmod. `jffs2_statfs()` reports flash-size-derived block counts and computes available space from dirty plus free space minus write-reserved blocks.

`jffs2_evict_inode()` drops page cache, clears the VFS inode, and calls `jffs2_do_clear_inode()` to free JFFS2 in-core state. `jffs2_iget()` builds an inode from on-flash data via `jffs2_do_read_inode()`, sets ownership, size, times, nlink, operations, and special inode data; directories recompute nlink by counting live child dirents.

`jffs2_dirty_inode()` persists metadata-only dirty state by constructing an `iattr` and calling `jffs2_do_setattr()`. `jffs2_do_remount_fs()` handles read-only restrictions, stops GC and flushes writebuffer when remounting, restarts GC for writable mounts, and forces `SB_NOATIME`.

`jffs2_new_inode()` allocates a VFS inode, initializes JFFS2 private state, applies gid inheritance and ACL pre-initialization, creates an inocache/raw inode via `jffs2_do_new_inode()`, fills VFS fields, and inserts the inode locked.

`jffs2_do_fill_super()` validates MTD type and geometry, rejects unsupported MLC NAND, sets flash/sector sizes, initializes flash-specific writebuffer behavior, allocates the inocache hash table, initializes xattrs, scans/builds the filesystem with `jffs2_do_mount_fs()`, obtains root inode 1, fills superblock fields, and starts GC for writable mounts. Cleanup unwinds xattr, summary, block, inode-cache, and flash setup state.

`jffs2_gc_fetch_inode()` and `jffs2_gc_release_inode()` are GC-specific inode lifetime helpers. Unlinked inodes are looked up with `ilookup()` to avoid resurrecting deleted objects; linked inodes use `jffs2_iget()`.

Key dependencies: VFS superblock/inode APIs, MTD geometry, mount/build/readinode/write paths, xattr/ACL/security hooks, writebuffer setup backends, and GC thread control.
