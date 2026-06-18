# File Research: sources/os/linux/linux-stable/fs/mnt_idmapping.c

## Purpose

Implements mount idmapping objects and conversions between kernel inode IDs, VFS IDs exposed through a mount, and filesystem user namespace IDs.

## Main Entry Points

- `make_vfsuid()` / `make_vfsgid()`: map filesystem `kuid_t`/`kgid_t` values into mount-relative `vfsuid_t`/`vfsgid_t`.
- `from_vfsuid()` / `from_vfsgid()`: map mount-relative IDs back into filesystem namespace IDs for inode writes.
- `vfsgid_in_group_p()`: checks group membership using VFS GIDs.
- `alloc_mnt_idmap()`: allocates and copies a user namespace UID/GID map for a mount.
- `mnt_idmap_get()` / `mnt_idmap_put()`: refcount mount idmaps.
- `statmount_mnt_idmap()`: emits mount idmap extents for statmount-style reporting.

## Control Flow And State

The file defines two global singleton idmaps: `nop_mnt_idmap`, an identity mapping, and `invalid_mnt_idmap`, a mapping that converts everything to invalid IDs. Fast paths return immediately for these singletons. Nontrivial mapping first translates through the filesystem user namespace when needed, then maps down or up through the mount’s copied UID/GID maps.

`alloc_mnt_idmap()` copies both UID and GID maps from a user namespace. Small maps are copied inline; large maps duplicate forward and reverse extent arrays. Refcount operations skip the two singletons. `statmount_mnt_idmap()` reports extents relative to the current caller’s user namespace and skips ranges that cannot be resolved for that caller.

## Dependencies

Depends on Linux user namespace UID/GID map internals, credential/group helpers, seq_file output, refcounting, and VFS ID wrapper types from mount idmapping headers.

## Risks

Mapping correctness depends on preserving uid/gid extent ordering and copying immutable namespace maps with the right memory barriers. Invalid or unmapped IDs intentionally propagate as invalid VFS/kernel IDs, and callers must handle those before writing inode ownership. Large map allocation has two arrays that must be freed consistently.
