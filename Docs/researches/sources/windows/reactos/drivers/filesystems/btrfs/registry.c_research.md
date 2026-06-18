# File Research: sources/windows/reactos/drivers/filesystems/btrfs/registry.c

## Purpose

`registry.c` manages WinBtrfs registry-backed configuration. It loads global mount defaults, per-volume mount overrides, mounted/unmounted state, UID/GID SID mappings, debug logging settings, and registry-change notifications.

## Main Responsibilities

- Load per-volume options under a UUID-named registry key.
- Mark volumes mounted or unmounted.
- Reset stale mounted state for volume subkeys on startup.
- Load Windows SID to Unix UID mappings.
- Load Windows SID to Unix GID mappings, creating a default BUILTIN\Users to gid `100` mapping on first run.
- Read and normalize global mount defaults.
- In debug builds, read and hot-reload debug log file/device settings.
- Register registry change notifications through a work item.

## Key Functions

- `registry_load_volume_options`: initializes `Vcb->options` from global defaults, then overlays values from the registry key for the filesystem UUID.
- `registry_mark_volume_mounted`: creates/opens the UUID key and writes `Mounted = 1`.
- `registry_mark_volume_unmounted_path`: either writes `Mounted = 0` if the key has other options, or deletes the UUID key if `Mounted` is the only value.
- `registry_mark_volume_unmounted`: builds the UUID registry path and delegates to `registry_mark_volume_unmounted_path`.
- `is_uuid`: validates UUID-shaped registry subkey names.
- `reset_subkeys`: enumerates UUID subkeys and marks them unmounted or deletes them.
- `read_mappings`: loads `Mappings` values into `uid_map_list`.
- `read_group_mappings`: loads `GroupMappings` into `gid_map_list`, and creates a default group mapping if the key is new.
- `get_registry_value`: helper that queries a value, copies it if type/size match, or writes the supplied default if missing or malformed.
- `read_registry`: primary global registry loader. It refreshes mappings, creates/opens the root key, optionally resets volume subkeys, loads mount defaults, and handles debug-only logging options.
- `registry_work_item`: worker callback invoked after registry changes; reloads settings and rearms notification.
- `watch_registry`: installs the initial `ZwNotifyChangeKey` callback.

## Configuration Values

Global and per-volume options include:

- `Compress`
- `CompressForce`
- `CompressType`
- `ZlibLevel`
- `ZstdLevel`
- `FlushInterval`
- `MaxInline`
- `SkipBalance`
- `NoBarrier`
- `NoTrim`
- `ClearCache`
- `AllowDegraded`
- `Readonly`
- `NoRootDir`
- `NoDataCOW`
- `SubvolId` for per-volume selection
- `Ignore` for per-volume ignore behavior
- `NoPNP` globally during non-refresh reads

The loader clamps some values:

- Compression type above ZSTD becomes `0`.
- `MaxInline` is capped to fit within the filesystem node layout.
- zlib level is capped at `9`.
- zstd level is capped at `ZSTD_maxCLevel()`.
- zero flush interval falls back to a default/global value.

## Registry Path Construction

Per-volume registry paths are built by appending a canonical UUID string to `registry_path`. The UUID formatter inserts hyphens after byte positions matching the standard `8-4-4-4-12` UUID display layout.

The same path construction is repeated in load, mounted, and unmounted functions.

## Mapping Behavior

`read_mappings` clears the current UID mapping list, opens or creates `\Mappings`, and enumerates `REG_DWORD` values. Each value name is treated as a SID string and the DWORD is treated as the mapped Unix UID.

`read_group_mappings` mirrors this for `\GroupMappings`. If the key is newly created, it writes a default `S-1-5-32-545 = 100`, corresponding to BUILTIN\Users as a conventional Unix `users` group.

Both mapping loaders are called under `mapping_lock` in `read_registry`.

## Debug Build Behavior

When `_DEBUG` is enabled, `read_registry` also manages:

- `DebugLogLevel`
- `LogDevice`
- `LogFile`

It compares old and new settings during refresh, closes/dereferences stale logging handles or device objects, and opens the new log target if needed. The default log file is `\??\C:\btrfs.log`.

## Notable Risks and Implementation Notes

- `get_registry_value` calls `ZwClose(h)` on allocation failure even though ownership remains with the caller; that helper should be audited because closing the caller’s handle inside a query helper is surprising.
- Registry string/path buffers are manually sized and not NUL-terminated in several places, which is valid for `UNICODE_STRING` but requires all consumers to respect explicit lengths.
- The mounted/unmounted logic preserves option-bearing UUID keys but deletes keys that only hold transient mounted state.
- `read_registry(refresh=false)` resets all UUID subkeys that look like volume IDs, which makes driver startup treat prior mounted state as stale.
- Registry notification is rearmed after each callback, using a global `WORK_QUEUE_ITEM`.
