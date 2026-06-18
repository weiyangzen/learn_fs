# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putfh.c

Purpose: implements `PUTFH`, installing a client-provided NFSv4 filehandle as the compound current filehandle and resolving it into either an MDS object or pNFS DS handle.

Important APIs and types: functions are `nfs4_ds_putfh`, `nfs4_mds_putfh`, `nfs4_op_putfh`, and no-op free. It uses `file_handle_v4`, `fsal_pnfs_ds`, `gsh_export`, `fsal_export`, `gsh_buffdesc`, `fsal_obj_handle`, and `compound_data_t`.

Control flow: top-level `nfs4_op_putfh` validates the wire FH with `nfs4_Is_Fh_Invalid`, allocates `data->currentFH` storage if needed, copies bytes into it, then dispatches to DS or MDS handling based on `nfs4_Is_Fh_DSHandle`. DS handling resolves the pNFS data server id through `pnfs_ds_get`, updates `op_ctx` with the DS and its MDS export, clears current entry, checks DS permissions if server/export changed, builds an FSAL DS handle via `pds->s_ops.make_ds_handle`, and marks the current file type regular. MDS handling resolves the export id, updates `op_ctx` export, clears current entry, checks export access if export changed, converts the opaque handle from wire to host with `wire_to_host`, creates an FSAL object handle, installs it as current entry, then drops the local ref.

State and persistence: mutates compound current FH/object/filetype and global per-request `op_ctx` export or pNFS DS context. It does not alter stable state or filesystem content.

Dependencies and integration: central integration point for filehandle encoding conventions, export manager, pNFS DS registry, FSAL handle digest/create APIs, access checks, credentials, and compound context cleanup.

Risks: input handle length is trusted after `nfs4_Is_Fh_Invalid`; MDS copies `fs_len` into a fixed `NFS4_FHSIZE` buffer and relies on validation. Export/DS context changes before later failures mean callers see the resolved context even on some errors. DS handles intentionally leave `current_obj` NULL, so later metadata ops must reject them.

Test signals: invalid FH, unknown export, unknown DS, export access denied/wrongsec, DS permission failure, `wire_to_host` failure, `create_handle` failure, successful MDS current object install, and DS current_ds install with regular file type.
