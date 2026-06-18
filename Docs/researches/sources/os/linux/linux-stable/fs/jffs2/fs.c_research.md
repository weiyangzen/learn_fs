# File Research: sources/os/linux/linux-stable/fs/jffs2/fs.c

## Role

Implements VFS-facing inode/superblock support: setattr, statfs, inode eviction/loading/creation, remount behavior, mount fill, GC inode access helpers, and flash-type setup/cleanup.

## Attribute Handling

- `jffs2_do_setattr()` writes a new metadata raw inode node for ownership, mode, time, and size changes.
- Special files and symlinks preserve their metadata payload:
  - device numbers are re-encoded;
  - symlink target is read from existing metadata node.
- File extension writes a zero-compressed hole node.
- Truncate-to-zero uses deletion allocation priority.
- Shrinking truncates the fragment tree under `f->sem`, then calls `truncate_setsize()` after releasing it.
- `jffs2_setattr()` uses `setattr_prepare()` and applies POSIX ACL chmod updates after mode changes.

## Inode Lifecycle

- `jffs2_iget()` reads an inode from raw nodes, fills VFS metadata, and installs operation tables by file type.
  - Symlinks use cached target.
  - Directories calculate link count from child directory dirents.
  - Device nodes read encoded device numbers from metadata.
- `jffs2_new_inode()` allocates a VFS inode and JFFS2 inode cache, handles setgid/default ACL behavior, calls `jffs2_do_new_inode()`, initializes timestamps and identity, and inserts it into the inode hash.
- `jffs2_evict_inode()` truncates page cache, clears the VFS inode, and clears JFFS2 inode-private state.
- `jffs2_dirty_inode()` converts datasync inode dirtiness into a JFFS2 metadata node rewrite.

## Superblock and Mount

- `jffs2_statfs()` reports flash-derived blocks and available space after reserved write blocks.
- `jffs2_do_remount_fs()` prevents remounting an internally read-only filesystem writable, flushes write buffers when transitioning, and starts/stops GC as needed.
- `jffs2_do_fill_super()`:
  - rejects unsupported MLC NAND;
  - rejects NAND/DataFlash when writebuffer support is absent;
  - aligns flash size to erase size;
  - rejects too-small media;
  - sets cleanmarker size and flash-specific setup;
  - allocates inode cache hash table;
  - initializes xattrs and mounts/scans the filesystem;
  - loads root inode and sets superblock limits/time range;
  - starts GC for writable mounts.

## GC Helpers

- `jffs2_gc_fetch_inode()` gets inodes for GC, using `ilookup()` for unlinked inodes to avoid resurrecting absent deleted inodes.
- `jffs2_gc_release_inode()` drops the VFS inode reference.
- `jffs2_flash_setup()` and `jffs2_flash_cleanup()` dispatch to NAND, DataFlash, NOR write-buffer, and UBI setup/cleanup hooks.

## Research Notes

This file bridges raw JFFS2 log metadata with Linux VFS inode semantics. It is also the main mount setup path, constructing the in-memory eraseblock/inocache world before exposing the root dentry.
