# File Research: sources/os/linux/linux/fs/befs/linuxvfs.c

## Purpose
Linux VFS integration for the BeFS driver. It registers the filesystem, mounts read-only block devices, builds VFS inodes from BeFS inodes, implements lookup/readdir through B+trees, maps file blocks for reads, handles symlinks, exports file handles, parses mount options, and reports filesystem stats.

## Filesystem Registration
- Defines `befs_fs_type` with:
  - name `befs`
  - `FS_REQUIRES_DEV`
  - `kill_block_super`
  - fs_context operations
- `init_befs_fs()` initializes the inode cache and registers the filesystem.
- `exit_befs_fs()` destroys cache and unregisters.

## VFS Operations
- Super operations:
  - inode allocation/free
  - put_super
  - statfs
  - show_options
- Directory operations:
  - `generic_read_dir`
  - `befs_readdir`
  - `generic_file_llseek`
  - `generic_setlease`
- Directory inode ops:
  - `befs_lookup`
- Address-space ops:
  - `befs_read_folio`
  - `befs_bmap`
- Symlink address-space ops:
  - `befs_symlink_read_folio`

## File Reading
- `befs_get_block()` rejects writes (`create` returns `-EPERM`), maps file logical blocks using `befs_fblock2brun()`, and fills a mapped buffer head.
- Regular files use `generic_ro_fops`.

## Directory Handling
- `befs_lookup()` optionally converts dentry names from mounted NLS charset to UTF-8, searches the directory B+tree, and instantiates the found inode.
- `befs_readdir()` iterates B+tree entries by ordinal `ctx->pos`, optionally converts UTF-8 names to NLS, and emits directory entries.

## Inode Loading
- `befs_iget()`:
  - maps Linux inode number to BeFS inode address
  - reads raw inode block
  - validates with `befs_check_inode()`
  - applies uid/gid mount overrides or disk ownership
  - synthesizes atime/ctime from BeFS modified time
  - handles short symlink inline storage
  - converts datastreams for regular files, directories, and long symlinks
  - computes `i_blocks` via `befs_count_blocks()`
  - assigns VFS ops based on mode

## Mount and Superblock
- `befs_fill_super()`:
  - forces read-only if mounted writable
  - reads superblock at block 0, accounting for x86 512-byte offset vs PPC location
  - calls `befs_load_sb()` and `befs_check_sb()`
  - sets filesystem block size and VFS superblock ops
  - creates root dentry
  - loads requested or default NLS table
- `befs_reconfigure()` allows only read-only remount.
- `befs_put_super()` frees charset, unloads NLS, and releases private superblock.

## Mount Options
- `uid`
- `gid`
- `iocharset`
- `debug`

`befs_show_options()` prints non-default uid/gid, charset, and debug option.

## Export Support
Defines export operations using generic file-handle helpers and BeFS inode lookup. Parent lookup uses stored BeFS parent metadata.

## Notable Risks
- `befs_get_parent()` calls `befs_iget()` with `befs_ino->i_parent.start`; this is a narrow use of the block-run field and is worth checking against intended BeFS parent address semantics.
- NLS conversion allocates per lookup/readdir name and returns `-EILSEQ` on unconvertible characters.
- Filesystem is explicitly read-only; attempts to map write blocks are denied.
