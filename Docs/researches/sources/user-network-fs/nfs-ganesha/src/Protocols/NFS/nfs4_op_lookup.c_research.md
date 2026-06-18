# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookup.c

Purpose: implements NFSv4 `LOOKUP`, resolving a name in the current directory and replacing the compound current filehandle/object with the result.

Important APIs and types: uses `LOOKUP4args/res`, `fsal_obj_handle`, `fsal_status_t`, exports, and junction state. It calls `nfs4_sanity_check_FH`, `nfs4_utf8string_scan`, `fsal_lookup`, `export_ready`, `set_op_context_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `nfs4_FSALToFhandle`, and `set_current_entry`.

Control flow: the current FH must be a directory; if the check reports notdir on a symlink, the result is converted to `NFS4ERR_SYMLINK`. The target name is validated as a single UTF-8 path component, then `fsal_lookup` returns a referenced object. If the found object is a directory with a `junction_export`, the handler crosses the pseudo-filesystem junction: it verifies export readiness, switches `op_ctx` to the target export, checks access, hides inaccessible exports as `NFS4ERR_NOENT`, handles `WRONGSEC`, obtains the target export root object, and replaces the looked-up junction object with the root. Finally it converts the object to an NFSv4 filehandle, updates `data->currentFH` and `data->current_obj`, and drops the local ref.

State and persistence: mutates compound current object/FH and operation export context. It does not change filesystem contents or NFS state.

Dependencies and integration: central to pathname traversal, pseudo-fs junction exports, export access control, FSAL lookup, filehandle encoding, and LTTng.

Risks: export lock/reference ordering around junction traversal is critical. Access-denied hiding must match READDIR visibility. On errors after `set_op_context_export`, the compound context remains at the crossed export, which may be intended for junction errors but must be consistent.

Test signals: lookup in non-directory, symlink current FH, invalid name, missing name, normal file/directory lookup, junction crossing success, inaccessible junction hidden as NOENT, WRONGSEC, stale export, and filehandle encoding failure.
