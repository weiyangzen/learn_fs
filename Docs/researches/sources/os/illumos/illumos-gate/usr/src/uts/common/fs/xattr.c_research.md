# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/xattr.c

## Scope

Implements the illumos generic extended-attribute/system-attribute vnode layer. The file provides GFS-backed synthetic XATTR directories and synthetic system-attribute files, while passing through ordinary extended-attribute operations to an underlying filesystem-provided XATTR directory when present.

Read completely: 1,758 lines.

## Core Model

Solaris/illumos exposes extended attributes as a special directory reached with `LOOKUP_XATTR`. This module handles the cases where system attributes are enabled, with or without real filesystem extended attributes:

- SYSATTR + XATTR: creates a translucent GFS directory that merges synthetic system attribute entries with entries from the real filesystem XATTR directory.
- SYSATTR only: creates a GFS-only directory containing system attribute view files.
- XATTR only: returns the underlying filesystem XATTR directory directly.
- Neither: returns `EINVAL`.

The synthetic directory contains two static entries:

- `VIEW_READONLY`, created by `xattr_mkfile_ro()`
- `VIEW_READWRITE`, created by `xattr_mkfile_rw()`

Each synthetic file stores an `xattr_view_t` and presents an XDR-encoded nvlist of selected file attributes.

## Main Entry Points

- `xattr_init()` builds vnode operation vectors for the synthetic xattr directory and system-attribute files.
- `xattr_dir_lookup()` is the public lookup path used by VFS lookup with `LOOKUP_XATTR`; it creates, races, or reuses `dvp->v_xattrdir`.
- `xattr_dir_vget()` reconstructs a synthetic xattr directory or sysattr file from an `xattr_fid_t`.
- `xattr_mkfile()`, `xattr_mkfile_ro()`, and `xattr_mkfile_rw()` create synthetic sysattr view vnodes.
- `xattr_sysattr_casechk()` detects case-insensitive name conflicts between real xattrs and reserved sysattr names.

## System Attribute File Operations

The `xattr_file_tops` vnode operations implement synthetic regular files:

- `xattr_file_open()` and `xattr_file_access()` reject writes to readonly views.
- `xattr_file_close()` clears locks and shares.
- `xattr_file_getattr()` fabricates regular-file attributes, copies ctime/mtime from the parent xattr directory, and computes file size by packing the nvlist.
- `xattr_file_read()` builds an nvlist using `xattr_fill_nvlist()`, packs it as XDR, and moves it to userspace.
- `xattr_file_write()` unpacks an XDR nvlist and applies mutable attributes through `VOP_SETATTR()` on the real parent object.
- `xattr_common_fid()` builds a fid from the real parent fid plus a synthetic directory/file offset.
- `xattr_file_pathconf()` reports no nested xattrs or sysattrs for the synthetic files.

`xattr_fill_nvlist()` maps illumos `f_attr_t` names to `xvattr_t` requests, obtains attributes from the real parent object, and emits nvlist entries. It handles boolean optional attributes, create time, generation, fsid, antivirus scanstamp, reparse/offline/sparse flags, and ephemeral owner/group SIDs via kidmap.

`xattr_file_write()` validates nvpair names, types, view mutability, and VFS support for ephemeral IDs before setting `xvattr_t` fields. It accepts boolean values, uint64 arrays, uint8 arrays, and nested SID nvlists.

## Directory Operations

The `xattr_dir_tops` vnode operations implement the synthetic/translucent directory:

- `xattr_dir_realdir()` lazily looks up and caches the underlying real XATTR directory, retaining its hold until inactive.
- `xattr_dir_open()` and `xattr_dir_close()` reject write-open and pass open/close to the real xattr directory if it exists.
- `xattr_dir_getattr()` uses real xattr directory attributes when available; otherwise fabricates a sticky world-writable directory and copies selected parent attributes.
- `xattr_dir_setattr()` forwards setattr to the real xattr directory when present; transient GFS-only setattr changes are ignored.
- `xattr_dir_access()` rejects write access to the synthetic directory and otherwise delegates to the real xattr directory when present.
- `xattr_dir_create()` forbids creating real xattrs with reserved sysattr names and can create the real xattr directory with `CREATE_XATTR_DIR`.
- `xattr_dir_remove()` forbids removing reserved sysattr entries and passes through real xattr removal.
- `xattr_dir_link()` rejects links from synthetic system-attribute files and passes other links to the real xattr directory.
- `xattr_dir_rename()` copies sysattrs when either endpoint is a reserved sysattr name; otherwise it renames in the real xattr directory.
- `xattr_dir_readdir()` emits static GFS sysattr entries first, then reads the real xattr directory if present.
- `xattr_dir_realvp()` exposes the cached real xattr directory.
- `xattr_dir_inactive()` releases the cached real xattr vnode and frees the GFS directory object.

`xattr_lookup_cb()` supports `gfs_vop_lookup()` by looking through the real xattr directory after static GFS entries are checked.

## State And Dependencies

Important local structures:

- `xattr_file_t`: `gfs_file_t` plus `xattr_view_t`.
- `xattr_dir_t`: `gfs_dir_t` plus cached `xattr_realvp`.

The implementation depends on VFS/vnode operations, GFS directory helpers, `xvattr_t` optional attributes, nvlist XDR packing, kidmap SID/ID mapping, pathname helpers, and vnode flags including `V_SYSATTR`, `V_XATTRDIR`, `VFS_XATTR`, `VFS_XID`, and `VFSFT_XVATTR`.

## Invariants And Risks

- Synthetic sysattr names are reserved. Real xattrs with exact reserved names are rejected, and case conflicts can be flagged in readdir.
- `LOOKUP_HAVE_SYSATTR_DIR` is critical in `xattr_dir_realdir()` to avoid recursive xattr lookup.
- Cached `xattr_realvp` lifetime is tied to the synthetic GFS directory and must be released only at inactive.
- The GFS xattr directory creation path handles races by destroying the loser vnode manually and using the existing `dvp->v_xattrdir`.
- Sysattr fid generation depends on parent fids plus stable synthetic offsets.
- `xattr_file_write()` has delicate nvlist cleanup paths; early returns after unpacking must free the nvlist to avoid leaks.
