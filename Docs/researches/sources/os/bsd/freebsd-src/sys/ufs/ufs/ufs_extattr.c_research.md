# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_extattr.c

## Purpose
Implements UFS extended attribute support for the backing-file based UFS1 extended attribute system. It manages per-mount EA lifecycle, optional autostart, enabling/disabling named attributes, and vnode operations for get/set/delete.

## Key Contents
Compiled under `#ifdef UFS_EXTATTR`.

- Feature registration:
  - `FEATURE(ufs_extattr, "ufs extended attribute support")`
- Sysctl:
  - `debug.ufs_extattr_sync`
  - Forces synchronous writes for attribute metadata/content when enabled.
- Per-mount lock helpers:
  - `ufs_extattr_uepm_lock`
  - `ufs_extattr_uepm_unlock`
- Attribute validation/search:
  - `ufs_extattr_valid_attrname`
    - Rejects null and empty names.
  - `ufs_extattr_find_attr`
    - Finds enabled backing attribute by namespace/name under mount EA lock.
- Per-mount lifecycle:
  - `ufs_extattr_uepm_init`
    - Initializes list, lock, and `INITIALIZED` flag.
  - `ufs_extattr_uepm_destroy`
    - Requires initialized but not started state.
  - `ufs_extattr_start`
  - `ufs_extattr_start_locked`
    - Sets `STARTED` and stores held credential.
  - `ufs_extattr_stop`
    - Disables all enabled attributes, clears `STARTED`, releases credential.
- Optional autostart under `UFS_EXTATTR_AUTOSTART`:
  - `ufs_extattr_lookup`
    - Performs UFS lookup for a name under a directory.
  - `ufs_extattr_iterate_directory`
    - Iterates attribute backing files in a namespace directory and enables regular files.
  - `ufs_extattr_autostart`
  - `ufs_extattr_autostart_locked`
    - Applies only to UFS1.
    - Looks for `.attribute/system` and `.attribute/user` below filesystem root.
    - Starts EA support and enables found backing files.
- Enable/disable:
  - `ufs_extattr_enable_with_open`
    - Opens backing vnode read/write, increments writecount, references vnode, unlocks it, then enables.
  - `ufs_extattr_enable`
    - Validates backing vnode type and started state.
    - Ensures no duplicate attribute.
    - Reads and validates `ufs_extattr_fileheader` magic/version.
    - Adds enabled attribute entry to per-mount list.
  - `ufs_extattr_disable`
    - Removes enabled attribute entry and closes backing vnode.
- Control API:
  - `ufs_extattrctl`
    - Requires `PRIV_UFS_EXTATTRCTL`.
    - Rejects jailed privileged callers via `priv_check`.
    - Supports only UFS1 because UFS2 uses native extended attributes.
    - Handles start, stop, enable, disable commands.
- Vnode operations:
  - `ufs_getextattr`
    - Locks per-mount EA state and calls `ufs_extattr_get`.
  - `ufs_setextattr`
    - Rejects null `uio` delete legacy behavior.
    - Calls `ufs_extattr_set`.
  - `ufs_deleteextattr`
    - Calls `ufs_extattr_rm`.
- Attribute record get:
  - `ufs_extattr_get`
    - Requires started state and non-empty name.
    - Checks extattr read credentials.
    - Finds backing attribute.
    - Allows only offset 0.
    - Computes backing-file offset as file header plus inode-indexed fixed-size record.
    - Reads per-inode `ufs_extattr_header`.
    - Requires `INUSE` and matching inode generation.
    - Returns size and optionally copies content.
- Attribute record set:
  - `ufs_extattr_set`
    - Rejects readonly mounts, stopped EA state, invalid names, invalid credentials.
    - Rejects nonzero offset and content larger than configured backing slot.
    - Writes per-inode header with `INUSE`, content length, and inode generation.
    - Writes user data after header.
    - Uses `IO_SYNC` if configured.
- Attribute record delete:
  - `ufs_extattr_rm`
    - Rejects readonly mounts, stopped state, invalid names, invalid credentials.
    - Validates current header is in-use and generation matches.
    - Clears `INUSE` and length in backing header.
- Inactive cleanup:
  - `ufs_extattr_vnode_inactive`
    - When EA support is started, removes all enabled attributes for an inactive vnode.

## Interactions
- ACL code uses this layer for POSIX.1e and NFSv4 ACL storage.
- UFS2 is explicitly excluded from backing-file `extattrctl` because UFS2 uses native extended attributes.
- Uses vnode read/write/open/close operations against backing files.
- Per-inode records rely on inode number and generation to detect stale attribute data reuse.
