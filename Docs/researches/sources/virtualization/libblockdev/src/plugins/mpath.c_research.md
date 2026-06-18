# File Research: sources/virtualization/libblockdev/src/plugins/mpath.c

## Role
Implements the libblockdev multipath plugin. It combines `multipath` and `mpathconf` command wrappers with direct libdevmapper queries to identify multipath maps and member devices.

## Main Dependencies
- GLib and blockdev utilities.
- `libdevmapper` for listing DM maps, checking target type, and retrieving dependencies.
- `/dev/block/<major>:<minor>` symlinks for dependency device-name resolution.
- Runtime tools `multipath >= 0.4.9` and `mpathconf`.

## Availability
- `bd_mpath_is_tech_avail()` gates base query/modify support on `multipath`.
- Friendly-name modification is query-rejected and gated on `mpathconf`.

## Operations
- `bd_mpath_flush_mpaths()` runs `multipath -F`, then verifies `multipath -ll` returns no devices; any remaining output is reported as `BD_MPATH_ERROR_FLUSH`.
- `bd_mpath_is_mpath_member(device)` lists all DM maps, filters maps whose first target type is `multipath`, enumerates each map's dependencies, and compares resolved dependency device names to the input device.
- `bd_mpath_get_mpath_members()` returns a NULL-terminated list of all dependency device names for multipath maps, reporting progress through blockdev utilities.
- `bd_mpath_set_friendly_names(enabled)` runs `mpathconf --find_multipaths y --user_friendly_names y/n --with_multipathd y`.

## Internal Helpers
- `get_device_name()` resolves a major:minor number through `/dev/block`.
- `map_is_multipath()` uses `DM_DEVICE_STATUS` and the first target type.
- `get_map_deps()` uses `DM_DEVICE_DEPS`, converts dependency device numbers to major:minor strings, and resolves them to device names.

## Error Notes
- DM task failures map to `BD_MPATH_ERROR_DM_ERROR`.
- Invalid `/dev/block` symlink formats map to `BD_MPATH_ERROR_INVAL`.
- Dependency lookup can fail for permission/root-related reasons and is surfaced accordingly.

## Filesystem/Storage Relevance
Multipath devices are stable block-device abstractions over multiple physical paths. This plugin identifies member devices and flushes/configures maps that may sit below filesystems, LVM, or MD RAID.
