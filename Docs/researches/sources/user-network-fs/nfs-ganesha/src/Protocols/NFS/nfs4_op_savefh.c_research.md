# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_savefh.c

## Purpose
Implements NFSv4 SAVEFH and helper `set_saved_entry`. It snapshots CurrentFH-related object, export, pNFS DS, file type, permissions, and current stateid for later RESTOREFH or operations that use SavedFH.

## Important APIs, Types, and Functions
- `set_saved_entry` manages saved object replacement and old saved object/DS release.
- `nfs4_op_savefh` handles `NFS4_OP_SAVEFH`.
- Uses `nfs4_sanity_check_FH`, `nfs4_AllocateFH`, `export_ready`, `get_gsh_export_ref`, `put_gsh_export`, `pnfs_ds_get_ref`, `pnfs_ds_put`, `save_op_context_export_and_set_export`, and `restore_op_context_export`.
- `nfs4_op_savefh_Free` is a no-op.

## Control Flow
SAVEFH validates CurrentFH, allocates SavedFH storage if necessary, checks/export-refs the current export, copies FH bytes, updates saved object through `set_saved_entry` when different, saves current stateid validity and value, drops old saved export and pNFS DS refs, then stores current export permissions and pNFS DS refs. `set_saved_entry` temporarily switches op context to the saved export when releasing a previous saved object/DS, clears saved stateid validity, releases old resources, refs the new object, and records file type.

## State and Persistence Behavior
Mutates compound saved state only. It manages references on saved object, export, pNFS DS, and DS handle. It preserves a saved stateid snapshot for restore and later SavedFH-based operations.

## Dependencies and Integration Points
Tightly paired with RESTOREFH and operations such as RENAME that consume SavedFH. Relies on export readiness/refcounting, FSAL object refs, pNFS DS lifetimes, and op-context switching for correct release semantics.

## Risks
Reference ordering is the major risk: old saved export/DS/object must be released after new refs are acquired or while the right op context is active. Saved DS handles are not separately refcounted in the same way as pNFS DS objects, so equality checks matter.

## Test Signals
Test repeated SAVEFH on same object and different objects, saving after PUTFH/LOOKUP across exports, pNFS DS handle saving, subsequent RESTOREFH, SavedFH use by RENAME, stale export handling, and leak/refcount checks.
