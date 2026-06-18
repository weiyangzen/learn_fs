# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_restorefh.c

## Purpose
Implements NFSv4 RESTOREFH. It replaces CurrentFH and current compound context with the filehandle, object, export, pNFS DS, file type, and stateid snapshot saved by SAVEFH.

## Important APIs, Types, and Functions
- `nfs4_op_restorefh` handles `NFS4_OP_RESTOREFH`.
- Uses `nfs4_Is_Fh_Empty`, `nfs4_sanity_check_saved_FH`, `export_ready`, `get_gsh_export_ref`, `set_op_context_export`, `set_current_entry`, and `pnfs_ds_get_ref`.
- `nfs4_op_restorefh_Free` is a no-op.

## Control Flow
The handler clears the response, checks that SavedFH exists, sanity-checks the saved filehandle, takes a new export reference if the saved export is still ready, copies saved FH bytes into CurrentFH, restores export permissions and pNFS DS context, points the current entry at `saved_obj`, restores saved stateid validity/value, and handles DS-handle current fields.

## State and Persistence Behavior
Mutates only compound/request context. It changes CurrentFH, current object reference, current export context, pNFS DS reference, file type, and current stateid. It does not alter persistent filesystem or client state.

## Dependencies and Integration Points
Depends on SAVEFH creating a coherent snapshot. It integrates with export refcounting, op context export management, pNFS data-server refs, filehandle helpers, and compound stateid tracking.

## Risks
RESTOREFH assumes saved export/object lifetimes are valid and refcounted. If saved export is no longer ready, it returns stale. DS-handle handling only updates `current_ds` fields when `data->current_ds != NULL`, so mixed DS/non-DS restore paths need coverage.

## Test Signals
Test missing SavedFH, stale saved export, normal save/restore around LOOKUP or PUTFH, saved stateid restoration, pNFS DS restore, export permission restoration, and object reference balance under repeated SAVEFH/RESTOREFH.
