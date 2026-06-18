# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo.c

## Purpose
Implements NFSv4 SECINFO for a named child of the current directory. It resolves the target, crosses junctions when needed, checks export access, builds the ordered security flavor list, and clears CurrentFH for minorversion greater than 0.

## Important APIs, Types, and Functions
- `nfs4_op_secinfo` handles `NFS4_OP_SECINFO`.
- Uses `nfs4_utf8string_scan`, `nfs4_sanity_check_FH`, `fsal_lookup`, `export_ready`, `save_op_context_export_and_set_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `check_resp_room`, and `set_current_entry`.
- Builds `secinfo4` entries for RPCSEC_GSS privacy/integrity/none when GSS is compiled, plus AUTH_UNIX and AUTH_NONE from export permissions.
- `nfs4_op_secinfo_Free` frees the allocated `SECINFO4resok_val`.

## Control Flow
The handler validates the name and CurrentFH directory, looks up the child object, checks for a directory junction under `jct_lock`, refs the junction export when ready, and if crossing a junction saves/restores op context while running export access checks and replacing the child object with the junction export root. ACCESS hides the export as NOENT, while WRONGSEC is expected and still allows reporting security info. It counts enabled security entries, checks response room, allocates the result array, fills flavors in preferred order, and for v4.1+ clears CurrentFH and export context as required by SECINFO semantics.

## State and Persistence Behavior
No persistent state changes occur. It temporarily mutates op context during junction traversal and may clear CurrentFH/current export for minorversion greater than 0. It owns and frees the result flavor array.

## Dependencies and Integration Points
Depends on export permissions, GSS compile-time support, FSAL lookup/root-entry access, pseudo/junction metadata, request credential rebuilding, response sizing, and current filehandle management.

## Risks
Junction traversal must not leak export references or leave altered credentials. ACCESS is intentionally converted to NOENT for hidden exports. Response-size estimation must include GSS OID payloads. v4.1+ CurrentFH clearing is protocol-visible and can affect following compound ops.

## Test Signals
Test normal child SECINFO, invalid name, non-directory CurrentFH, missing child, junction to allowed export, junction ACCESS hidden as NOENT, WRONGSEC export, GSS and non-GSS builds, response overflow, v4.0 CurrentFH retention, and v4.1 CurrentFH clearing.
