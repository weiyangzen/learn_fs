# File Research: sources/os/linux/linux-stable/fs/f2fs/namei.c

## Purpose

`namei.c` implements F2FS namespace operations for the Linux VFS: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, whiteout, parent lookup, and inode operation tables. It also applies F2FS-specific inode creation policy such as extension-based hot/cold classification, compression inheritance, inline-data setup, project quota inheritance, encryption preparation, and inline xattr/dentry setup.

## Extension and Temperature Policy

- `is_extension_exist()`
  - Matches filename extensions case-insensitively.
  - Supports wildcard `"*"`.
  - Handles temporary-extension matching for patterns such as media files with an additional temp suffix.

- `is_temperature_extension()`
  - Uses relaxed temporary-extension matching for hot/cold data classification.

- `is_compress_extension()`
  - Uses stricter dot-aware matching for compression allow/deny extension lists.

- `f2fs_update_extension_list()`
  - Adds or removes hot/cold extension entries in `raw_super->extension_list`.
  - Maintains cold count in little-endian `extension_count` and hot count in `hot_ext_count`.
  - Preserves layout where cold extensions precede hot extensions.
  - Rejects duplicates, missing removals, and full extension lists.

- `set_file_temperature()`
  - Marks newly created files cold or hot based on superblock extension lists, unless extension identification is disabled.

## Compression Policy for New Inodes

- `set_compress_new_inode()`
  - Applies only when compression is supported.
  - Directories inherit compression/no-compression policy.
  - Regular files may be excluded if their filename matches a hot extension.
  - `nocompress` extensions override compression.
  - `compress` extensions enable compression context.
  - Otherwise compression flags may be inherited from the parent directory.

## Inode Creation

- `f2fs_new_inode()`
  - Allocates a VFS inode and an F2FS nid.
  - Initializes owner, timestamps, generation, directory depth, project quota, encryption, quota state, and F2FS inode flags.
  - Sets `FI_NEW_INODE`, optional `FI_EXTRA_ATTR`, `FI_INLINE_XATTR`, `FI_INLINE_DENTRY`, `FI_PROJ_INHERIT`, `FI_INLINE_DATA`, and encryption state.
  - Computes inline xattr size from flexible-inline-xattr support and mount options.
  - Inherits masked F2FS flags from parent and sets indexed directory flag for directories.
  - Initializes extent tree and emits `trace_f2fs_new_inode()`.
  - On failure, marks the inode bad and, if needed, marks `FI_FREE_NID` so later cleanup can return the nid.

## VFS Namespace Operations

- `f2fs_create()`
  - Checks checkpoint error and checkpoint readiness.
  - Initializes parent quota.
  - Creates a regular file inode, assigns file operations, and adds a directory entry under `f2fs_lock_op()`.
  - Completes nid allocation with `f2fs_alloc_nid_done()`.
  - Instantiates the dentry and performs dirsync if required.

- `f2fs_link()`
  - Prepares fscrypt link context.
  - Enforces project quota inheritance compatibility.
  - Increments link state through `FI_INC_LINK`.
  - Adds a new directory entry for an existing inode.
  - Rolls back link increment and inode reference on failure.

- `f2fs_get_parent()`
  - Resolves `..` by looking up `dotdot_name` and returning an alias for the parent inode.

- `f2fs_lookup()`
  - Validates name length.
  - Prepares encrypted/casefolded lookup name.
  - Finds the directory entry and loads the inode.
  - Rejects zero-link inodes as corruption.
  - Verifies encryption context compatibility for encrypted directory children.
  - Avoids negative dentry caching for Unicode casefolded directories.

- `f2fs_unlink()`
  - Finds the target entry, validates link count invariants, acquires orphan inode capacity, deletes the entry, and optionally invalidates casefolded dentries.
  - Marks serious link-count inconsistencies as `SBI_NEED_FSCK`.

- `f2fs_get_link()`
  - Wraps `page_get_link()` and treats empty symlink content as broken, returning `-ENOENT`.

- `f2fs_symlink()`
  - Prepares encrypted symlink target if required.
  - Creates symlink inode and directory entry.
  - Encrypts and writes symlink data.
  - Flushes symlink data to reduce broken symlink risk after power loss.
  - Unlinks the dentry on data-write failure after instantiation.

- `f2fs_mkdir()`
  - Creates a directory inode with dir operations and nofs mapping GFP mask.
  - Uses `FI_INC_LINK` while adding the directory entry.
  - Instantiates and optionally dirsyncs.

- `f2fs_rmdir()`
  - Delegates to `f2fs_unlink()` only if `f2fs_empty_dir()` succeeds.

- `f2fs_mknod()`
  - Creates special inode, initializes device type, adds link, and instantiates.

- `__f2fs_tmpfile()`
  - Shared implementation for tmpfile and whiteout creation.
  - Creates unlinked regular or whiteout inode.
  - Acquires orphan inode slot and adds the inode to the orphan list.
  - For whiteouts, marks inode linkable for rename whiteout handling.
  - For real tmpfiles, calls `d_tmpfile()` when a file is available.

- `f2fs_tmpfile()`
  - Public VFS tmpfile hook.
  - Checks checkpoint state and calls `finish_open_simple()`.

- `f2fs_create_whiteout()`
  - Creates a whiteout inode for `RENAME_WHITEOUT`.

- `f2fs_get_tmpfile()`
  - Helper for creating an unlinked regular inode without a `struct file`.

## Rename Paths

- `f2fs_rename()`
  - Handles normal rename, replacement, and whiteout.
  - Checks checkpoint state, project quota inheritance compatibility, quotas, and inline-dir conversion where needed.
  - If replacing an existing inode:
    - Ensures replaced directory is empty.
    - Repoints the new entry to the old inode.
    - Decrements replaced inode link count and manages orphan entry.
  - If not replacing:
    - Adds a new link in the destination directory.
    - Updates destination directory link count for directory moves.
  - Updates old inode parent tracking or marks lost parent ino.
  - Deletes the old entry.
  - Adds whiteout at the old name if requested.
  - Updates `..` for moved directories.
  - Adds strict-fsync transition directory ino entries when configured.
  - Dirsyncs when either directory requires it.

- `f2fs_cross_rename()`
  - Implements `RENAME_EXCHANGE`.
  - Locates both entries and, for directory operands crossing parents, locates both `..` entries.
  - Checks project quota inheritance on both sides.
  - Computes parent link-count adjustments for file/directory exchanges across directories.
  - Swaps directory entries and updates parent ino metadata.
  - Updates directory link counts and strict-fsync tracking.

- `f2fs_rename2()`
  - Validates supported flags: `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`.
  - Runs `fscrypt_prepare_rename()`.
  - Dispatches to exchange or normal rename.
  - Emits rename tracepoints.

## Symlink and Inode Operation Tables

- `f2fs_encrypted_get_link()`
  - Reads symlink page and calls `fscrypt_get_symlink()`.

- `f2fs_encrypted_symlink_getattr()`
  - Combines F2FS getattr with fscrypt symlink size adjustment.

- Operation tables:
  - `f2fs_encrypted_symlink_inode_operations`
  - `f2fs_dir_inode_operations`
  - `f2fs_symlink_inode_operations`
  - `f2fs_special_inode_operations`

## Consistency and Recovery Hooks

- Namespace mutations are guarded by checkpoint error/readiness checks.
- Operations that alter metadata use `f2fs_lock_op()` where appropriate.
- Deletions/replacements acquire orphan inode capacity before removing links.
- Dirsync directories trigger `f2fs_sync_fs()`.
- Strict fsync mode records transitioned directories for recovery.
- Corruption signals set `SBI_NEED_FSCK` and return `-EFSCORRUPTED`.
