# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vfs.h

## Role

`vfs.h` defines illumos' central virtual filesystem mount abstraction. It supplies the `vfs_t` structure, filesystem identifiers, mount-option tables, VFS operation signatures, filesystem type switch records, VFS feature bits, mount/root operation enums, and kernel helper prototypes used by filesystem implementations and the generic VFS layer.

## Key Interfaces

The file defines:
- `fsid_t`, the two-word filesystem identifier used in `statvfs` and mount lookup.
- `fid_t` and `fid32_t`, fixed-size file identifiers used by stateless file servers and `VFS_VGET`.
- `mntopt_t` and `mntopts_t`, mount-option name/value tables with flags such as `MO_SET`, `MO_HASVALUE`, `MO_NODISPLAY`, and `MO_IGNORE`.
- `vfs_t`, the per-mounted-filesystem object, including global and per-zone mount-list links, `vfs_op`, covered vnode, flags, block size, type index, fsid, private data, device, refcount, resource/mountpoint strings, zone ownership, FEM hooks, and lofi mount ID.
- `vfs_impl_t`, private kernel-side data for feature bitmaps, vnode-operation statistics, high-resolution creation time, and zone references.
- `VFS_OPS`, the canonical VFS operation signature macro used to define `struct vfsops` and the operation-registration union in `vfs_opreg.h`.

The VFS operation set includes `mount`, `unmount`, `root`, `statvfs`, `sync`, `vget`, `mountroot`, `freevfs`, `vnstate`, and `syncfs`. Public macros such as `VFS_MOUNT()` and `VFS_STATVFS()` route through generic `fsop_*` wrappers rather than directly indexing `vfs_op`.

## Flags and Features

Mount flags include policy and state bits such as `VFS_RDONLY`, `VFS_NOSETUID`, `VFS_REMOUNT`, `VFS_UNMOUNTED`, `VFS_XATTR`, `VFS_NODEVICES`, `VFS_NOEXEC`, `VFS_STATS`, and `VFS_XID`.

Feature bits are 64-bit `vfs_feature_t` values and are accessed through `vfs_has_feature()`, `vfs_set_feature()`, and related helpers. Feature examples include extended attributes, case-insensitive behavior, ACL-on-create support, dirent flags, system attribute views, access-filtered dirents, reparse points, and zero-copy cache-buffer support.

## Integration Points

`vfssw_t` and `vfsdef_t` define filesystem-type registration. `vfssw_t` holds the installed filesystem name, init function, flags, mount-option prototype, reference count, lock, and VFS operation vector. `vfsdef_t` is the module-facing filesystem definition record, with version `VFSDEF_VERSION = 5`.

Kernel prototypes cover mount/unmount control, root configuration, VFS locking, global sync, mount list management, option parsing, mountpoint/resource strings, vfssw lookup/refcounting, feature propagation, filesystem ID creation, mounted-device lookup, lofi access, and zone-safety checks.

## Research Notes

This header is a contract boundary. Filesystems should use accessor/helper functions for operation vectors, option tables, mount lists, and reference counts; comments explicitly warn that several fields are private to the generic VFS layer. Changes here affect filesystem modules, mount tools, vnode statistics, zone-visible mount behavior, and kernel ABI expectations.
