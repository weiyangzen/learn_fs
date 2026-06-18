# File Research: sources/os/linux/linux/fs/mnt_idmapping.c

## Purpose
Implements mount idmapping objects and conversion helpers between filesystem kernel IDs, VFS IDs, and mount-relative IDs. This supports idmapped mounts where UID/GID ownership exposed through a mount may differ from the filesystem’s internal user namespace mapping.

## Main Responsibilities
- Define `struct mnt_idmap` with UID/GID maps and a reference count.
- Provide global identity and invalid mount idmaps.
- Map `kuid_t`/`kgid_t` into `vfsuid_t`/`vfsgid_t` for userspace-visible results.
- Map `vfsuid_t`/`vfsgid_t` back into filesystem `kuid_t`/`kgid_t`.
- Allocate, reference, and free mount idmaps copied from user namespaces.
- Render mount ID mappings for statmount output.

## Key Objects
- `nop_mnt_idmap`: identity mapping used for non-idmapped mounts.
- `invalid_mnt_idmap`: mapping where all IDs are invalid.
- `struct mnt_idmap`: contains `uid_map`, `gid_map`, and `refcount_t count`.

## Key Functions
- `make_vfsuid()` maps a filesystem `kuid_t` through the filesystem user namespace and down through the mount UID map.
- `make_vfsgid()` does the same for groups.
- `from_vfsuid()` maps a mount-visible VFS UID up through the mount UID map and into the filesystem user namespace.
- `from_vfsgid()` does the same for groups.
- `vfsgid_in_group_p()` checks whether a VFS GID is among the caller’s groups, or always succeeds without `CONFIG_MULTIUSER`.
- `copy_mnt_idmap()` copies a user namespace UID/GID map, including dynamically allocated extent arrays for large maps.
- `alloc_mnt_idmap()` allocates a mount idmap from a user namespace.
- `mnt_idmap_get()` / `mnt_idmap_put()` manage references, skipping global identity/invalid maps.
- `statmount_mnt_idmap()` serializes UID or GID map extents relative to the caller’s current user namespace.

## Important Behaviors and Edge Cases
- Identity map fast paths return direct wrapped kernel IDs.
- Invalid map fast paths return invalid VFS or kernel IDs.
- Initial filesystem idmapping avoids `from_kuid()`/`from_kgid()` overhead by using raw values.
- `copy_mnt_idmap()` refuses to copy an unwritten map with zero extents.
- Memory ordering in `copy_mnt_idmap()` pairs with user namespace map publication.
- Dynamic extent arrays are freed only when `nr_extents > UID_GID_MAP_MAX_BASE_EXTENTS`.
- `statmount_mnt_idmap()` skips mappings that cannot be resolved in the caller’s user namespace and returns `-EAGAIN` on seq-file overflow.

## Dependencies
- User namespace UID/GID mapping internals.
- `map_id_down()`, `map_id_up()`, and `map_id_range_up()`.
- VFS ID wrapper types from `linux/mnt_idmapping.h`.
- Seq-file output for statmount.

## Research Notes
This file is core infrastructure for idmapped mounts. It deliberately keeps raw VFS ID initialization private to this implementation, so external users construct VFS IDs only through checked mapping functions.
