# File Research: sources/windows/winbtrfs/src/registry.c

## Purpose

`registry.c` manages WinBtrfs driver configuration stored in the Windows registry. It loads global mount defaults, per-volume mount options, mounted/unmounted volume markers, SID-to-UID and SID-to-GID mappings, debug logging settings, and registry change notifications.

The file is kernel-mode registry plumbing around `ZwCreateKey`, `ZwOpenKey`, `ZwQueryValueKey`, `ZwEnumerateValueKey`, `ZwSetValueKey`, `ZwDeleteValueKey`, and `ZwNotifyChangeKey`.

## Per-Volume Mount Options

`registry_load_volume_options` builds a per-volume registry path by appending the filesystem UUID to `registry_path`. It initializes `Vcb->options` from global `mount_*` defaults, then opens the UUID key and enumerates values.

Recognized per-volume values include:

- `Ignore`
- `Compress`
- `CompressForce`
- `CompressType`
- `Readonly`
- `ZlibLevel`
- `FlushInterval`
- `MaxInline`
- `SubvolId`
- `SkipBalance`
- `NoBarrier`
- `NoTrim`
- `ClearCache`
- `AllowDegraded`
- `ZstdLevel`
- `NoRootDir`
- `NoDataCOW`

It clamps compression type to valid Btrfs compression IDs, clamps max inline data to the node-size-derived maximum, limits zlib level to 9, limits ZSTD level to `ZSTD_maxCLevel()`, and restores a default flush interval if the registry value is zero.

## Mounted State Tracking

`registry_mark_volume_mounted` creates or opens the per-UUID volume key and writes `Mounted=1`.

`registry_mark_volume_unmounted_path` opens a volume key, enumerates its values, and decides whether to clear or delete it. If any option other than `Mounted` exists, it writes `Mounted=0`; otherwise it deletes the key completely. This preserves user options while removing empty transient volume keys.

`registry_mark_volume_unmounted` builds the UUID path and calls `registry_mark_volume_unmounted_path`.

`is_uuid` validates registry subkey names with the canonical 36-character UUID shape and hyphen positions.

`reset_subkeys` enumerates UUID-shaped subkeys, copies their names into a temporary list, then calls `registry_mark_volume_unmounted_path` for each. This is used during non-refresh startup to mark previous mount records as unmounted without modifying non-volume registry subkeys.

## User and Group Mapping Reads

`read_mappings` loads `registry_path\Mappings`. It first clears `uid_map_list`, freeing SIDs and mapping nodes, then opens/creates the key and enumerates REG_DWORD values. Each value name is interpreted as a SID string and the DWORD data as a UID, passed to `add_user_mapping`.

`read_group_mappings` mirrors this for `registry_path\GroupMappings` and `gid_map_list`. If the group mapping key is newly created, it adds a default mapping for `S-1-5-32-545` (`BUILTIN\Users`) to GID `100`, writes it into the registry, and calls `add_group_mapping`.

Both mapping lists are protected by `mapping_lock` in `read_registry`.

## Generic Registry Defaulting

`get_registry_value` queries a named value. If the value exists with the expected type and sufficient length, it copies the data into the caller-provided storage. If the type or length is wrong, it deletes and recreates the value with the current in-memory default. If the value is missing, it creates it from the current in-memory default.

This makes `read_registry` both a reader and a registry default materializer.

## Global Registry Load

`read_registry` is the main global configuration loader. It:

- Acquires `mapping_lock`, refreshes UID/GID mappings, then releases it.
- Creates/opens the root driver registry key.
- Calls `reset_subkeys` on initial load, not refresh.
- Reads or initializes global values:
  - `Compress`
  - `CompressForce`
  - `CompressType`
  - `ZlibLevel`
  - `FlushInterval`
  - `MaxInline`
  - `SkipBalance`
  - `NoBarrier`
  - `NoTrim`
  - `ClearCache`
  - `AllowDegraded`
  - `Readonly`
  - `ZstdLevel`
  - `NoRootDir`
  - `NoDataCOW`
  - `NoPNP` on initial load only
- Ensures `mount_flush_interval` is not zero.

In `_DEBUG` builds it also manages debug logging values:

- Reads `DebugLogLevel`.
- Reads `LogDevice` and, on refresh or state transitions, resets `comfo`, `comdo`, and `log_handle` under `log_lock`, then tries `IoGetDeviceObjectPointer` when device logging is enabled.
- Reads or creates `LogFile`, defaulting to `\??\C:\btrfs.log`.
- Reopens the log file with `ZwCreateFile` when debug logging state changes and no log device is active.

Old `UNICODE_STRING` buffers for log device/file are freed after refresh transitions.

## Registry Watcher

`registry_work_item` is a delayed work queue callback. It reloads the registry with `refresh=true`, then re-arms `ZwNotifyChangeKey` for `REG_NOTIFY_CHANGE_LAST_SET`.

`watch_registry` initializes the global `WORK_QUEUE_ITEM wqi` and registers the first `ZwNotifyChangeKey` notification.

## Dependencies and Shared State

The file uses global configuration variables declared elsewhere, including `registry_path`, `mount_*` defaults, `no_pnp`, `uid_map_list`, `gid_map_list`, `mapping_lock`, and debug-only log handles/device pointers. It depends on helper functions such as `hex_digit`, `add_user_mapping`, and `add_group_mapping`.

## Error Handling and Notes

Most registry errors are logged and either returned or cause the relevant optional section to stop. Some mapping enumeration loops ignore intermediate errors other than `STATUS_NO_MORE_ENTRIES`, so malformed individual values are skipped rather than fatal. Registry strings and key paths are manually allocated with pool memory and freed in local cleanup paths.

The mounted-state logic is intentionally conservative: per-volume keys containing user options persist after unmount, but optionless keys are deleted.
