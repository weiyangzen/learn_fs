# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_get.c

## Role
Implements the ZCP property getter `zfs.get_prop(dataset, property)`. It resolves dataset type, validates property applicability, handles user/system/userquota/written properties, pushes value and source to Lua, and converts recoverable missing-property cases into no pushed values.

## Dataset Type And Source Helpers
- `get_objset_type()` maps snapshots to `ZFS_TYPE_SNAPSHOT` and objset types to filesystem or volume.
- `get_objset_type_name()` returns `"snapshot"`, `"filesystem"`, or `"volume"`.
- `get_prop_src()` pushes nil for readonly/version properties, `"default"` for empty setpoint, or the setpoint string otherwise.
- `zcp_handle_error()` treats `ENOENT` as nonfatal/no values, and turns invalid properties, I/O errors, or unexpected errors into Lua errors.

## User And ZAP Properties
- `zcp_get_user_prop()` holds the dataset, uses `dsl_prop_get_ds()` with `ZAP_MAXVALUELEN`, and pushes string value plus setpoint.
- `get_zap_prop()` reads regular inheritable properties from DSL property storage, handles string/numeric/index types, applies temporary kernel-only properties where available, and pushes value plus source.

## Special System Properties
- `get_dsl_dir_prop()` directly reads dsl_dir accounting values such as usedsnap, usedchild, usedds, usedrefreserv, and logicalused under `dd_lock`.
- `get_special_prop()` handles computed or nonstandard properties: ratios, used/referenced/available/logical values, clones list, creation/createtxg/guid/unique/objsetid, origin, useraccounting, written, type, previous snapshot, name, mountpoint, ZPL version, deferred destroy/userrefs, filesystem/snapshot counts, remaptxg, clone count, inconsistent flag, ivset guid, receive resume token, volsize, and volblocksize.
- `prop_valid_for_ds()` rejects unsupported/hidden cases such as iSCSI options, mounted, origin on non-clones, and properties invalid for dataset type.
- `zcp_get_system_prop()` holds the dataset, validates applicability, tries special direct handling, then falls back to ZAP-backed property lookup.

## Userquota And Written Properties
- `get_userquota_prop()` classifies user/group quota/used prefixes.
- Kernel-only `parse_userquota_prop()` parses numeric ids or SID-style domain/rid forms.
- Kernel-only `zcp_get_userquota_prop()` creates a temporary `zfsvfs_t`, calls `zfs_userspace_one()`, and pushes quota/used value plus dataset source.
- `parse_written_prop()` expands `written@snap` relative names to full snapshot names.
- `zcp_get_written_prop()` holds current and old snapshot datasets, calls `dsl_dataset_space_written()`, and pushes used bytes plus dataset source.

## Library Entry
- `zcp_get_prop()` dispatches by property kind: user property, userquota property, `written@`, known system property, or invalid-name Lua error.
- `zcp_load_get_lib()` registers `get_prop` in the already-created `zfs` table.

## Important Details
- Successful lookups push two Lua return values: value and source.
- Missing/non-applicable properties return zero Lua values rather than an errno to Lua.
- Several fatal paths longjmp through Lua; callers with allocations must use ZCP cleanup handlers where applicable.
- Userquota support is compiled only for kernel mode.
