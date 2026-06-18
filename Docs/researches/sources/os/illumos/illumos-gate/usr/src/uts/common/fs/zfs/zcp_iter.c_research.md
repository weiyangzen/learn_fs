# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_iter.c

## Role
Implements the ZCP `zfs.list` submodule. It exposes Lua iterator factories for clones, snapshots, children, user properties, and visible system properties.

## Iterator Pattern
- Each list function validates arguments through `zcp_parse_args()` via `zcp_list_func()`.
- Iterators are returned as Lua closures with cursor/object state captured in upvalues.
- Dataset holds are short-lived per iteration step, avoiding long-held references across Lua code.

## Clone Iterator
- `zcp_clones_list()` requires a snapshot, captures its dataset object id and cursor 0, and returns `zcp_clones_iter()`.
- `zcp_clones_iter()` opens the snapshot by object id, reads `ds_next_clones_obj` with a serialized ZAP cursor, advances the cursor, opens each clone object, and returns the clone dataset name.

## Snapshot Iterator
- `zcp_snapshots_list()` rejects snapshot inputs and captures filesystem/volume dataset object id.
- `zcp_snapshots_iter()` appends `@`, calls `dmu_snapshot_list_next()`, updates cursor upvalue, and returns full snapshot names.

## Child Iterator
- `dataset_name_hidden()` hides names containing `$` or `%`.
- `zcp_children_list()` rejects snapshot inputs and captures dataset object id.
- `zcp_children_iter()` calls `dmu_dir_list_next()` until a non-hidden child is found, updates cursor upvalue, and returns child names.

## Property Iterators
- `zcp_props_list()` holds the dataset, calls `dsl_prop_get_all()`, stores the nvlist pointer in Lua userdata, attaches a metatable, and returns `zcp_props_iter()`.
- `zcp_props_iter()` walks nvlist pairs, yields only user properties as `(name, value, source)`, and frees the nvlist at iteration end.
- `zcp_props_list_gc()` frees the nvlist if Lua garbage collects the userdata before natural iteration completion.
- `zcp_dataset_props()` builds an nvlist of visible, valid system property names for a dataset.
- `zcp_system_props_list()` returns that property-name list as a Lua table.

## Library Loading
- `zcp_load_list_lib()` creates the `zfs.list` table and registers `children`, `snapshots`, `properties`, `clones`, and `system_properties`.
- Functions needing cleanup get a Lua metatable with `__gc`.

## Important Details
- Channel programs run in the global zone, so dataset visibility filtering only hides internal `$`/`%` names.
- Clone iteration tolerates the source snapshot disappearing by ending iteration on `ENOENT`.
- The property iterator returns only user-defined properties; system property enumeration is separate.
