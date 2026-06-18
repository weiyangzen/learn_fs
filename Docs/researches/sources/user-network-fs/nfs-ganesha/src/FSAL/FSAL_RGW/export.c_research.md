# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/export.c

## Purpose
Implements RGW FSAL export operations: release, path lookup, wire-handle normalization, handle reconstruction, dynamic filesystem info, and export-op initialization.

## Important APIs, Types, and Functions
Functions: `release`, `lookup_path`, `wire_to_host`, `create_handle`, `get_fs_dynamic_info`, and `export_ops_init`. Types include `rgw_export`, `rgw_handle`, `rgw_file_handle`, `rgw_fh_hk`, and `rgw_statvfs`.

## Control Flow
`lookup_path` parses root/bucket/bucket-directory forms, rejects trailing slashes, calls `rgw_lookup`, fetches attributes, normalizes fsid in the non-mount2 path, constructs a handle, and returns optional attrs. `create_handle` validates `rgw_fh_hk`, calls `rgw_lookup_handle`, gets attrs, and constructs a handle. Dynamic info maps `rgw_statfs` counters. Release unmounts RGW, deconstructs root, detaches export, and frees resources.

## State and Persistence Behavior
Runtime export state includes mounted `rgw_fs`, root handle, and credentials. Persistent object state lives in RGW; wire handles are compact lookup keys.

## Dependencies and Integration Points
Depends on librgw/rgw_file APIs, FSAL common helpers, POSIX stat conversion, and sibling `construct_handle`, `deconstruct_handle`, and `rgw2fsal_error`.

## Risks
The bucket/global-directory path split leaks the duplicated string. Path parsing is ad hoc. Root/bucket attribute behavior differs by `USE_FSAL_RGW_MOUNT2`. `release` asserts unmount success. Access keys and secrets are held as plain strings in memory.

## Test Signals
RGW mount, root/bucket/directory lookup, handle wire/create round trips, statfs mapping, stale/error conversion, and clean unmount/release.
