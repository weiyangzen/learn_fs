# File Research: sources/os/linux/linux-stable/fs/ceph/util.c

## Purpose
Provides non-inline CephFS utility helpers for file layout conversion/validation and mapping VFS open flags to Ceph file modes/capabilities.

## Main Interfaces
- `ceph_file_layout_is_valid()`
- `ceph_file_layout_from_legacy()`
- `ceph_file_layout_to_legacy()`
- `ceph_flags_to_mode()`
- `ceph_caps_for_mode()`

## Behavior
Layout validation requires nonzero stripe unit/object size, 64 KiB alignment, object size as a multiple of stripe unit, and nonzero stripe count. Legacy conversion maps old wire layout fields to the modern layout and treats an all-zero legacy layout as no pool by setting `pool_id = -1`.

Open flags are translated into Ceph file modes, including directory pin and lazy I/O where supported. File modes are then expanded into required Ceph caps for read, write, buffer, cache, auth, xattr, and lazy I/O access.

## Integration Points
Used by mount/open/layout code and capability acquisition paths to normalize layout metadata and requested access.

## Risks And Review Focus
- Layout validation protects OSD striping assumptions; relaxing alignment/multiplicity checks would affect object mapping.
- Mode-to-cap mapping determines how much authority the client requests from MDS.
