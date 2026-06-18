# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_link.c

Purpose: implements NFSv4 `LINK`, creating a hard link to the saved filehandle object under the current directory filehandle.

Important APIs and types: uses `LINK4args`, `LINK4res`, `fsal_obj_handle`, `fsal_attrlist`, and `fsal_status_t`. It calls `nfs4_sanity_check_FH`, `nfs4_sanity_check_saved_FH`, `nfs4_utf8string_scan`, `fsal_link`, `fsal_get_changeid4`, `nfs4_Errno_status`, and FSAL attr prepare/release helpers.

Control flow: the current FH must be a directory and the saved FH must not be a directory. Cross-export hard links are rejected with `NFS4ERR_XDEV`. The new name is scanned as one UTF-8 path component. The handler captures pre-change information, calls `fsal_link(saved_obj, current_dir, name, pre_attrs, post_attrs)`, then fills `change_info4` from FSAL-provided pre/post change attributes when available, falling back to `fsal_get_changeid4` for `after`. The `atomic` flag is true only when both pre and post change attrs are valid.

State and persistence: persists a directory entry/hard link through the FSAL. It does not modify NFSv4 open/lock state directly, but it changes filesystem namespace and directory change ids.

Dependencies and integration: depends on compound `SAVEFH`/current FH semantics, export identity in `op_ctx` and `data->saved_export`, FSAL link implementation, NFS status conversion, and LTTng change-info tracing.

Risks: cross-export detection relies on export ids already set in compound context. Saved FH sanity uses `-DIRECTORY` to reject directories; behavior for special files depends on `nfs4_sanity_check_saved_FH`. Change info quality depends on FSAL attr support.

Test signals: missing current/saved FH, current not directory, saved directory, cross-export link, invalid UTF-8/path component, FSAL link errors, and accurate before/after/atomic cinfo.
