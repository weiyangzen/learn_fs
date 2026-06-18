# File Research: sources/os/linux/linux-stable/fs/befs/linuxvfs.c

This is the BeFS Linux VFS integration layer. It registers the filesystem, mounts block devices read-only, creates VFS inodes from BeFS inodes, implements directory lookup/readdir through BeFS B+trees, supports symlinks, handles NLS filename conversion, and exposes NFS export operations.

Major VFS objects:
- `befs_sops`: inode allocation/free, `put_super`, `statfs`, `show_options`.
- `befs_dir_operations`: generic read dir, `befs_readdir`, llseek, lease handling.
- `befs_dir_inode_operations`: lookup.
- `befs_aops`: read folio and bmap for regular files.
- `befs_symlink_aops`: read folio for long symlinks.
- `befs_export_operations`: file-handle encode/decode and parent lookup.
- `befs_fs_type`: block-device filesystem registration.

Important flows:
- File reads use `befs_read_folio()` -> `block_read_full_folio()` -> `befs_get_block()`.
- `befs_get_block()` rejects writes, maps logical blocks through `befs_fblock2brun()`, and calls `map_bh()`.
- `befs_lookup()` converts requested names to UTF-8 when NLS is active, searches the directory B+tree, and loads the returned inode block with `befs_iget()`.
- `befs_readdir()` repeatedly calls `befs_btree_read()` by `ctx->pos`, converts UTF-8 to NLS if configured, and emits entries.
- `befs_iget()` reads an inode block, validates it, populates mode, uid/gid overrides, timestamps, block accounting, file operations, directory operations, or symlink operations.
- `befs_symlink_read_folio()` reads long symlinks from datastreams and NUL-terminates the loaded page.
- `befs_parse_param()` handles `uid`, `gid`, `iocharset`, and `debug`; reconfigure ignores parsed options.
- `befs_fill_super()` reads the superblock at PPC or x86 offset, validates it, forces read-only mode, sets block size and operations, creates the root dentry, and loads NLS.
- `befs_reconfigure()` only permits remount read-only.
- Module init creates the inode cache and registers the filesystem.

Integration:
- Calls lower-level BeFS modules: `btree.c`, `datastream.c`, `inode.c`, `super.c`, and `io.c`.
- Uses Linux `fs_context`, buffer heads, block mapping helpers, NLS APIs, exportfs helpers, and slab inode caches.

Risk notes:
- The filesystem has no write support; `befs_get_block(create=1)` returns `-EPERM`, and mount forces `SB_RDONLY`.
- `befs_get_parent()` passes `befs_ino->i_parent.start` to `befs_iget()` instead of converting the full allocation-group address with `iaddr2blockno()`, which is suspicious for nonzero allocation groups.
- `show_options()` prints `charset=...`, while parser accepts `iocharset`; this may be user-visible inconsistency.
- Filename conversion allocates per lookup/readdir item and can fail with `-EILSEQ`.
- Mount validation rejects dirty/journaled filesystems rather than replaying journals.
