# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putrootfh.c

Purpose: implements `PUTROOTFH`, setting the compound current filehandle to the root of the NFSv4 pseudo filesystem.

Important APIs and types: uses `PUTROOTFH4res`, `fsal_obj_handle`, `gsh_export`, and `fsal_status_t`. It calls `set_current_entry`, `get_gsh_export_by_pseudo`, `set_op_context_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `nfs4_FSALToFhandle`, and FSAL ref helpers.

Control flow: the handler clears the response struct, sets `resop`, clears any current entry, fetches the export for pseudo path `/`, and sets it in `op_ctx`. If no export is available it returns `NFS4ERR_NOENT`. It checks export access; plain access denial returns error without exposing the pseudo root, and other access setup failures are logged. It obtains the root FSAL object for the pseudo root export, installs it as current entry, drops the local ref, converts it into `data->currentFH`, and returns `NFS4_OK`.

State and persistence: mutates the compound current object/FH and request export context. No filesystem data or NFSv4 state is changed.

Dependencies and integration: foundational for path traversal from the pseudo root, export manager lookup by pseudo path, credentials/access setup, FSAL root object retrieval, and filehandle encoding.

Risks: `memset(resp, 0, sizeof(*resp))` assumes no previous response allocations are live for the same slot. Root export reference handling is delegated to `set_op_context_export`; callers must not leak the export ref returned by `get_gsh_export_by_pseudo`. Filehandle encoding failure after setting current entry leaves current object installed with error status.

Test signals: missing pseudo root export, access denied, wrong credentials/access setup failure, FSAL root lookup failure, filehandle encoding failure, and successful current FH/object/export installation.
