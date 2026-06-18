# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_set.c

## Role
Implements ZCP support for setting dataset properties, currently limited to user properties.

## Main Logic
- `zcp_set_user_prop()` holds the dataset, builds a single-property nvlist, calls `dsl_props_set_sync_impl()` with local source, frees the nvlist, and releases the dataset.
- `zcp_set_prop_check()` rejects non-user properties, creates a single string-property nvlist, and validates it through `dsl_props_set_check()`.
- `zcp_set_prop_sync()` retrieves the channel program run info for the pool and applies user-property sync if the property is a user property.

## Important Details
- System/non-user property setting is intentionally not supported here; comments indicate future support would need `zfs_valid_proplist()`.
- The check path and sync path are designed for use through `zcp_synctask.c`'s generic sync-task wrapper.
- `zcp_dataset_hold()` may longjmp on hold errors; sync code assumes the ZCP runtime handles fatal Lua unwinding.
