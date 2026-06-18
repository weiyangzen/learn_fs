# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo_no_name.c

## Purpose
Implements NFSv4.1 SECINFO_NO_NAME for the current object or its parent, returning security flavors from the active export permissions and clearing CurrentFH.

## Important APIs, Types, and Functions
- `nfs4_op_secinfo_no_name` handles `NFS4_OP_SECINFO_NO_NAME`.
- Uses `nfs4_sanity_check_FH`, optional `nfs4_op_lookupp` for `SECINFO_STYLE4_PARENT`, `check_resp_room`, `set_current_entry`, and `clear_op_context_export`.
- Builds `secinfo4` arrays using the same flavor ordering as SECINFO.
- `nfs4_op_secinfo_no_name_Free` frees allocated results on success.

## Control Flow
The operation validates that a CurrentFH exists, optionally invokes LOOKUPP to replace CurrentFH with the parent, counts enabled GSS/AUTH entries from `op_ctx->export_perms`, checks response room, allocates and fills the result array, clears CurrentFH and current export context, sets `resp->resop`, and returns status.

## State and Persistence Behavior
No persistent filesystem state changes occur. The operation intentionally clears CurrentFH and releases current export context after successful result construction. Parent style may mutate CurrentFH before flavor collection through LOOKUPP.

## Dependencies and Integration Points
Depends on LOOKUPP semantics, export permission bits, GSS build options, response room tracking, and compound filehandle state management.

## Risks
Because it delegates parent-style lookup to `nfs4_op_lookupp` using the same response union location, `resp->resop` must be reset on error. Clearing CurrentFH is required but can surprise following compound operations if applied on the wrong status path.

## Test Signals
Test current and parent styles, missing CurrentFH, LOOKUPP failure at pseudo root or inaccessible parent, flavor list ordering, GSS and AUTH combinations, response overflow, CurrentFH clearing, and result free behavior.
