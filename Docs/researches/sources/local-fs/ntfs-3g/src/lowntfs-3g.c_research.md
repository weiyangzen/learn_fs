# File Research: sources/local-fs/ntfs-3g/src/lowntfs-3g.c

## Purpose

Implementation of the `lowntfs-3g` low-level FUSE NTFS driver. It maps FUSE inode operations directly to libntfs-3g inode, attribute, directory, security, xattr, reparse-point, and volume APIs.

This file is the main executable driver for the low-level variant built by `src/Makefile.am`.

## High-Level Architecture

- Uses FUSE low-level API through `fuse_lowlevel.h`.
- Maintains a global `ntfs_fuse_context_t *ctx` holding mount options, volume, permissions, cache, stream, xattr, plugin, and open-file state.
- Converts FUSE inode `1` to NTFS `$Root` via `INODE(ino)`.
- Uses `struct open_file` records linked from `ctx->open_files` to track per-open cleanup requirements.
- Supports optional reparse plugins unless `DISABLE_PLUGINS` is set.
- Uses compile-time permission/cache modes derived from `LPERMSCONFIG`:
  - `KERNELACLS`
  - `KERNELPERMS`
  - `CACHEING`
- Registers a `struct fuse_lowlevel_ops ntfs_3g_ops` table with lookup, getattr, read/write, create/remove, xattr, ioctl, bmap, and lifecycle callbacks.

## Core Data Structures

- `fuse_fstype`
  - Tracks whether kernel support is absent, unknown, `fuse`, or `fuseblk`.
- `ntfs_fuse_fill_item_t`
  - Buffer node used to stage directory entries for low-level `readdir`.
- `ntfs_fuse_fill_context_t`
  - Directory-read state: buffer chain, request, inode, offset, plugin file handle, and filled flag.
- `struct open_file`
  - Per-open state:
    - inode number
    - unlink ghost parent/name id
    - close flags
    - plugin file info copy
    - doubly linked list pointers
- Close flags:
  - `CLOSE_GHOST`: remove deferred ghost hard link on release.
  - `CLOSE_COMPRESSED`: close compressed attribute through `ntfs_attr_pclose()`.
  - `CLOSE_ENCRYPTED`: fix EFS raw encrypted attribute.
  - `CLOSE_DMTIME`: delayed mtime update.
  - `CLOSE_REPARSE`: plugin-backed release required.

## Initialization and Mount Flow

- `main()`:
  - Ensures fds `0`, `1`, and `2` are open.
  - Rejects setuid/setgid use with external FUSE.
  - Drops privileges, sets locale, parses mount options.
  - Initializes `ctx` through `ntfs_fuse_init()`.
  - Parses NTFS/FUSE mount options with `parse_mount_options(ctx, &opts, TRUE)`.
  - Rejects unsafe duplicate mounts unless both existing and requested mounts are read-only.
  - Computes absolute mount point for junction resolution.
  - On Linux, detects/loads FUSE support, creates `/dev/fuse` if needed, and chooses `fuseblk` for block devices when available.
  - Opens NTFS volume through `ntfs_open()`.
  - Forces `ro` option when the volume falls back to read-only.
  - Applies `fuseblk` options including `blkdev` and block size.
  - Builds user/security mapping and xattr mapping.
  - Registers internal reparse plugins.
  - Mounts FUSE, daemonizes/logs, runs `fuse_session_loop()`, then unmounts and cleans up.
- `ntfs_fuse_init()` sets defaults:
  - current uid/gid
  - Linux streams interface defaults to xattr
  - `ATIME_RELATIVE`
  - `silent = TRUE`
  - `recover = TRUE`
- `ntfs_open()`:
  - Translates context options into `NTFS_MNT_*` flags.
  - Calls `ntfs_mount()`.
  - Sets sync/compression/show-hidden/show-system/ignore-case options.
  - Reads free-space and free-MFT-record accounting.
  - Optionally removes `hiberfil.sys` if hibernation removal is requested.

## FUSE Capability Setup

- `ntfs_init()` requests:
  - Mac x-times on Darwin.
  - `FUSE_CAP_DONT_MASK` when available, so filesystem can process umask.
  - `FUSE_CAP_POSIX_ACL` when configured for kernel ACLs.
  - `FUSE_CAP_BIG_WRITES` when requested and volume capacity is considered safe.
  - `FUSE_CAP_IOCTL_DIR` when available.

## Stat and Lookup Behavior

- `ntfs_fuse_statfs()` returns cluster-based block counts, free clusters, estimated inode counts, free MFT records, and `NTFS_MAX_NAME_LEN`.
- `ntfs_fuse_getstat()` converts an NTFS inode to POSIX `struct stat`:
  - Computes link count from MFT link count or `ntfs_dir_link_cnt()`.
  - Treats directories through `$I30` index allocation size.
  - Treats regular unnamed data through data size/allocated size.
  - Applies EFS raw apparent size when needed.
  - Detects Interix special files from system+hidden file content.
  - Dispatches reparse-point stat to plugins when enabled.
  - Applies UID/GID/mode from user mapping when present, otherwise global mount uid/gid.
  - Converts NTFS timestamps into platform-specific `struct stat` timestamp fields.
- `ntfs_fuse_lookup()` opens parent, optionally checks execute permission, resolves name with `ntfs_inode_lookup_by_mbsname()`, rejects inodes `0` and `1`, and replies with a filled `fuse_entry_param`.

## Directory Handling

- `ntfs_fuse_opendir()` validates access, handles reparse directory plugin open, allocates a fill context, and stores it in `fi->fh`.
- `ntfs_fuse_readdir()` builds a full chained list of directory-entry buffers on first use, then replies one buffer at a time.
- `ntfs_fuse_filler()`:
  - Skips DOS-only names.
  - Converts Unicode names to local multibyte strings.
  - Assigns stat mode based on NTFS directory entry type.
  - Uses plugin stat for reparse entries when available.
  - Truncates too-long names on Darwin/Solaris to avoid kernel/userland errors.
- `ntfs_fuse_releasedir()` frees staged buffers and calls plugin release if needed.

## Read, Write, Open, and Release

- `ntfs_fuse_open()`:
  - Opens inode and unnamed `$DATA` unless reparse-backed.
  - Checks requested read/write permissions when the filesystem is responsible.
  - Delegates reparse opens to plugins.
  - Marks future release work for compressed, encrypted, delayed-mtime, and reparse files.
  - Denies write opens for metadata files below `FILE_first_user`.
  - Allocates and links an `open_file` record.
- `ntfs_fuse_read()`:
  - Reads from reparse plugin or unnamed `$DATA`.
  - Clamps reads at file size or EFS raw padded size.
  - Loops until requested data is read or an error occurs.
  - Updates atime according to mount atime policy.
- `ntfs_fuse_write()`:
  - Writes through reparse plugin or unnamed `$DATA`.
  - Loops until all data is written.
  - Updates mtime/ctime unless delayed mtime suppresses immediate updates.
  - Sets archive bit on successful writes.
- `ntfs_fuse_release()`:
  - Runs plugin release, compressed close, EFS fixup, delayed mtime update.
  - Removes `.ghost-ntfs-3g-%020llu` hard-link placeholders for unlinked open files.
  - Unlinks the `open_file` record from `ctx->open_files`.

## Creation and Metadata Changes

- `ntfs_fuse_create()` is the common helper behind create, mknod, symlink, and mkdir:
  - Converts names/targets to NTFS Unicode.
  - Enforces `windows_names` restrictions.
  - Denies creation under `$Extend`.
  - Checks parent create permissions.
  - Computes POSIX mode after file/dir masks.
  - Allocates or inherits NTFS security IDs when mappings are active.
  - Delegates creation into reparse-point directories to plugins.
  - Calls `ntfs_create_device()`, `ntfs_create_symlink()`, or `ntfs_create()`.
  - Sets security attributes for cases where a security ID could not be allocated.
  - Sets archive bit, updates parent name cache, dirty flags, entry attributes, and parent timestamps.
- `ntfs_fuse_setattr()` dispatches to:
  - `ntfs_fuse_chmod()`
  - `ntfs_fuse_chown()`
  - `ntfs_fuse_chownmod()`
  - `ntfs_fuse_trunc()`
  - `ntfs_fuse_utimens()` or `ntfs_fuse_utime()`
- `ntfs_fuse_trunc()`:
  - Denies metadata truncation.
  - Checks write access when needed.
  - Delegates reparse truncation to plugins.
  - For compressed files, extends by writing a final zero rather than plain truncation when upsizing past initialized size.
  - Updates archive bit and mtime/ctime.
- Time setters implement POSIX ownership/write-access checks when permissions are not delegated to the kernel.

## Link, Rename, Unlink, and Ghost Files

- `ntfs_fuse_newlink()`:
  - Opens source and target parent.
  - Rejects hard links to directories when a FUSE entry reply is requested.
  - Checks target parent permissions.
  - Delegates linking into reparse directories when needed.
  - Calls `ntfs_link()`, updates parent cache, archive bit, ctime, and parent mtime/ctime.
- `ntfs_fuse_rm()`:
  - Denies removal from `$Extend`.
  - Resolves and opens target.
  - Denies unlinking metadata files.
  - Applies Solaris directory type checks and sticky-directory permission logic.
  - If target is open, creates one or more hidden ghost hard links in the unlink parent so NTFS storage survives until release.
  - Removes the requested name through plugin unlink or `ntfs_delete()`.
- `ntfs_fuse_rename()`:
  - Explicitly notes rename should be atomic but is not.
  - If destination exists, checks it is empty when directory-like, creates a temporary backup name, removes destination, links source into destination, removes source, then cleans backup or tries restoration.
  - If destination does not exist, links new name then removes old name.
- `ntfs_fuse_safe_rename()` and `ntfs_fuse_rename_existing_dest()` implement the temporary-name dance for existing destinations.

## Reparse and Special File Support

- Internal plugin registrations cover:
  - mount points
  - NTFS symlinks
  - LX symlinks
  - WSL AF_UNIX sockets
  - WSL FIFOs
  - WSL character devices
  - WSL block devices
- `junction_getstat()` and `junction_readlink()` expose junction/symlink reparse points as POSIX symlinks.
- `wsl_getstat()` exposes supported WSL reparse tags as POSIX socket/fifo/char/block modes, including device numbers from WSL EAs.
- Unsupported reparse points appear as symlinks with a generated target string like `unsupported reparse tag 0x...`.

## Extended Attributes and Streams

When `HAVE_SETXATTR` is enabled:

- Defines xattr namespace classes:
  - user
  - system
  - security
  - trusted
  - open namespace
- `xattr_namespace()` classifies names according to stream interface mode.
- `fix_xattr_prefix()` maps POSIX-visible xattr names to NTFS named `$DATA` stream names:
  - strips `user.` prefix for user namespace
  - prefixes system/security/trusted names with ntfs-3g internal prefix
  - leaves names unchanged in open namespace mode
- `ntfs_check_access_xattr()` centralizes access checks for internal xattrs and POSIX ACL xattrs.
- `ntfs_fuse_listxattr()` lists named stream-backed xattrs when stream mode permits.
- `ntfs_fuse_getxattr()`:
  - Intercepts system/internal attributes and POSIX ACL-like attributes through `ntfs_xattr_system_getxattr()`.
  - Otherwise reads named `$DATA` attributes as xattr values.
  - Supports Darwin resource-fork position semantics.
  - Applies EFS raw apparent size for encrypted nonresident attributes.
- `ntfs_fuse_setxattr()`:
  - Intercepts internal/system xattr writes.
  - Enforces namespace ownership/root rules.
  - Creates or replaces named `$DATA` attributes.
  - Handles `XATTR_CREATE` and `XATTR_REPLACE`.
  - Updates archive bit and ctime, fixes EFS attributes when raw mode is active.
- `ntfs_fuse_removexattr()`:
  - Blocks removal of protected internal xattrs such as ACL, attributes, EFS info, and timestamps.
  - Removes allowed system xattrs or named stream attributes.
  - Invalidates kernel cache for system xattr changes when caching and suitable FUSE support are present.

## IOCTL, BMAP, Sync, and Cleanup

- `ntfs_fuse_ioctl()` copies input data into a temporary buffer and calls `ntfs_ioctl()`, accounting for FUSE 2.x signed `cmd` forwarding.
- `ntfs_fuse_bmap()` maps file block indexes to device block indexes for nonresident, uncompressed, unencrypted data.
- `ntfs_fuse_fsync()` syncs the full NTFS device.
- `ntfs_close()` logs permission-cache stats, destroys security context, and unmounts the NTFS volume.
- `ntfs_fuse_destroy2()` calls `ntfs_close()` from FUSE teardown.

## Important Edge Cases

- Metadata files are protected from write-open, truncate, and unlink.
- Inodes `0` and `1` are never returned to FUSE lookup/readdir; FUSE inode `1` maps to NTFS `$Root`.
- Rename is not atomic despite best-effort recovery.
- Directory reads are staged in memory as chained buffers; rewind clears prior results.
- Open-unlink behavior relies on ghost hard links and may create multiple ghost names for the same inode if opened multiple times.
- FUSE caching behavior depends heavily on compile-time `LPERMSCONFIG`.
- External FUSE setuid/setgid-root execution is rejected as insecure.
- Unprivileged users cannot mount block devices with external FUSE.
- `remove_hiberfile` behavior can remove `hiberfil.sys` during mount preparation.
- xattr behavior changes substantially with stream-interface mode and platform-specific xattr conventions.

## Dependencies

- FUSE low-level API.
- libntfs-3g modules: bitmap, attrib, inode, volume, dir, unistr, layout, index, time, security, reparse, EA, object ID, EFS, xattrs, ioctl, plugins, misc/logging.
- Shared option parsing and mount helpers from `ntfs-3g_common.h` / `ntfs-3g_common.c`.

## Role in Source Tree

This is the low-level NTFS-3G filesystem implementation. It is the operational bridge between kernel FUSE requests and libntfs-3g’s NTFS metadata/data APIs, including permissions, xattrs, alternate streams, reparse points, special files, and mount lifecycle behavior.
