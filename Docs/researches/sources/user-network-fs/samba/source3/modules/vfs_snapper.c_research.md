# sources/user-network-fs/samba/source3/modules/vfs_snapper.c

## Purpose
`vfs_snapper.c` integrates Samba with Snapper over system DBus. It exposes Snapper snapshots as shadow copies, supports snapshot create/delete management hooks, and translates SMB `@GMT` timestamped paths into Snapper snapshot paths while denying writes into snapshots.

## Important APIs, Types, And Functions
- DBus model types: `struct snapper_dict`, `struct snapper_snap`, and `struct snapper_conf`.
- DBus utility functions: `snapper_dbus_str_encode`, `snapper_dbus_str_decode`, `snapper_dbus_conn_create`, `snapper_dbus_msg_xchng`, `snapper_type_check`, and unpack/pack helpers for configs, snapshots, create, delete, and list-at-time.
- Snapper management hooks: `snapper_snap_check_path`, `snapper_snap_create`, `snapper_snap_delete`, and `snapper_get_shadow_copy_data`.
- Path translation helpers: `snapper_gmt_strip_snapshot`, `snapper_get_snap_at_time_call`, `snapper_snap_path_expand`, and `snapper_gmt_convert`.
- VFS wrappers mirror `shadow_copy2` coverage for stat/lstat/fstatat/open/readlink/realpath/chdir/disk_free/quota/get_real_filename and mutating-operation denial.

## Control Flow
DBus calls are synchronous: create a private system-bus connection, pack a method call, send and block for a reply, validate the reply type and signature, unpack typed arrays/structs/dictionaries, then unref messages and close the connection. Config discovery calls Snapper `ListConfigs` and requires the share path to exactly match a Snapper mount. Shadow-copy listing calls `ListSnapshots`, skips the current snapshot entry, and formats labels in descending order. GMT path access converts `smb_fname->twrp` to Unix time, asks Snapper for snapshots at that exact time, builds `base/.snapshots/<id>/snapshot`, appends the requested path, and delegates the VFS operation on that converted path. Mutating wrappers return `EROFS`, `EXDEV`, or media-write-protected NTSTATUS when the source or target has a timestamp.

## State And Persistence
The module stores no long-lived VFS private state. Each operation opens a new private DBus connection so Snapper sees the correct effective UID. Persistent state is owned by Snapper and the filesystem under `.snapshots`.

## Dependencies And Integration Points
It depends on libdbus, Snapper's `org.opensuse.Snapper` DBus API, Samba VFS hooks, NTSTATUS utilities, and SMB timestamp handling. It registers as `snapper` and participates both in shadow-copy enumeration and snapshot management (`FSCTL_SRV_REQUEST_RESUME_KEY`/shadow-copy style operations via Samba hooks).

## Risks
- DBus operations are blocking and can add latency to metadata and snapshot path access.
- `snapper_get_conf_call()` only supports exact share-root to Snapper-config mount matches.
- The code maps only `error.no_permissions` explicitly; other DBus errors collapse to `NT_STATUS_UNSUCCESSFUL`.
- Timestamp lookup uses exact lower/upper time equality; snapshots with nearby but not exact times will not match.
- Path construction assumes Snapper's `.snapshots/<id>/snapshot` layout.
- Some error paths use `abort()` on allocation failure inside unpack loops.

## Test Signals
- With Snapper configured for the share root, list Previous Versions and verify labels exclude the current snapshot.
- Create and delete snapshots through Samba snapshot hooks and verify Snapper IDs/paths.
- Open/stat/read files through `@GMT` labels and verify conversion to `.snapshots/<id>/snapshot`.
- Attempt mutating operations through snapshot paths and verify read-only failures.
- Test DBus permission errors, missing Snapper service, no matching config, and no snapshot at exact time.
