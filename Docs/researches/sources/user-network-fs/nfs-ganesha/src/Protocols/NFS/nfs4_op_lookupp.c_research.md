# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookupp.c

Purpose: implements NFSv4 `LOOKUPP`, moving the compound current filehandle/object to the parent directory, including reverse traversal over pseudo-fs junctions.

Important APIs and types: uses `LOOKUPP4res`, `fsal_obj_handle`, `gsh_export`, and export locks. Calls include `nfs4_sanity_check_FH`, `nfs_export_get_root_entry`, `export_ready`, `set_current_entry`, `set_op_context_export`, `nfs4_export_check_access`, `fsal_lookupp`, and `nfs4_FSALToFhandle`.

Control flow: validates current FH as a directory. It gets the current export root and checks whether the current object is that root. If so, it handles reverse junction traversal: root of the top pseudo root returns `NFS4ERR_NOENT`; otherwise it obtains the parent export and junction object under `original_export->exp_lock`, sets the junction object as current, switches `op_ctx` to the parent export, and checks access. Inaccessible parent exports are hidden as `NFS4ERR_NOENT`. After reverse-junction handling, or for normal directories, it calls `fsal_lookupp` to resolve the parent. A returned parent object is converted to a filehandle and installed as current; null parent results clear current entry and map the FSAL status.

State and persistence: mutates compound current object/FH and export context only. No stable state or filesystem namespace changes.

Dependencies and integration: tied to pseudo-fs export graph, export readiness/reference management, FSAL parent lookup, and access checking.

Risks: lock ordering around clearing current entry and export locks is intentionally careful; regressions can deadlock cleanup paths. The comparison `data->current_obj == root_obj` depends on object identity, not equivalent handles. Errors after switching export context need consistent cleanup.

Test signals: root pseudo lookup parent returning NOENT, reverse junction to parent export, access-hidden parent, stale parent export, normal parent lookup, FSAL lookup parent failure, and filehandle encoding failure.
