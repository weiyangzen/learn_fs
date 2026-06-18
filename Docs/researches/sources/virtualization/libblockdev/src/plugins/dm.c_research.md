# File Research: sources/virtualization/libblockdev/src/plugins/dm.c

## Role

`dm.c` implements libblockdev's basic device-mapper plugin. It provides small wrappers for creating/removing linear maps and querying dm map/node metadata.

## Initialization and Dependencies

`bd_dm_init()` redirects libdevmapper logging through `redirect_dm_log()` and sets verbose logging based on `DEBUG`.

`bd_dm_close()` clears libdevmapper callbacks/verbosity and resets cached dependency availability.

Runtime dependency checking is centered on `dmsetup` with minimum version `1.02.93`, checked via `check_deps()`.

`bd_dm_is_tech_avail()` reports that the plugin supports map operations, but `BD_DM_TECH_MAP` requires `dmsetup`.

## Map Creation and Removal

`bd_dm_create_linear()` builds a dmsetup table of the form:

- start sector `0`
- user-provided sector length
- `linear`
- backing device
- offset `0`

It calls `dmsetup create <map_name> --table <table>`, optionally adding `-u <uuid>`.

`bd_dm_remove()` calls `dmsetup remove <map_name>`.

Both paths rely on external command execution through `bd_utils_exec_and_report_error()`.

## Query Helpers

`bd_dm_name_from_node()` reads `/sys/class/block/<dm_node>/dm/name`, strips trailing whitespace, and returns the map name. It rejects missing or empty node names.

`bd_dm_node_from_name()` resolves `/dev/mapper/<map_name>` through `bd_utils_resolve_device()` and returns the basename, typically `dm-N`.

`bd_dm_get_subsystem_from_name()` creates a `DM_DEVICE_INFO` libdevmapper task, loads device info, reads the dm UUID, and returns the prefix before the first `-`; empty UUIDs or UUIDs without a hyphen return an empty string.

`bd_dm_map_exists()` requires effective root, lists dm devices with `DM_DEVICE_LIST`, scans for the requested name, and optionally requires a live table and non-suspended active state via `DM_DEVICE_INFO`.

## Dependencies

- GLib for errors, strings, mutexes, and atomics.
- `libdevmapper` for task-based queries.
- `dmsetup` for create/remove operations.
- libblockdev utilities for command execution and device resolution.

## Notable Risks

- `bd_dm_create_linear()` shells out to `dmsetup` rather than using libdevmapper tasks, so command availability/version and external behavior matter.
- `bd_dm_map_exists()` sets an error when not root, but a normal "not found" result returns `FALSE` with no error.
- UUID subsystem parsing assumes the convention `subsystem-rest`.
