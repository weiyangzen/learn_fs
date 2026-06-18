# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setquota.c

Purpose: implements the RQUOTA `SETQUOTA` RPC handler for both the legacy and extended rquota protocol versions. The public entry point `rquota_setquota()` decodes the version-specific argument shape, normalizes it into path, quota id, quota type, and `sq_dqblk`, then delegates to `do_rquota_setquota()`.

Important APIs and types: `nfs_arg_t`, `nfs_res_t`, `setquota_rslt`, `sq_dqblk`, `fsal_quota_t`, `struct svc_req`, `struct gsh_export`, `check_handle_lead_slash()`, `get_gsh_export_by_tag()`, `get_gsh_export_by_pseudo()`, `get_gsh_export_by_path()`, `set_op_context_export()`, `nfs_req_creds()`, and `exp->fsal_export->exp_ops.set_quota()`.

Control flow: the handler defaults to user quota, chooses extended arguments when `req->rq_msg.cb_vers == EXT_RQUOTAVERS`, otherwise uses the legacy `sqa_uid` style. The helper initializes the result to `Q_EPERM`, validates and normalizes the quota path, locates an export by tag, pseudo path, or real path depending on the supplied path and `mount_path_pseudo`, installs the export into `op_ctx`, obtains request credentials, copies wire quota fields into an FSAL quota structure, calls the FSAL `set_quota` operation, maps `ERR_FSAL_NO_QUOTA` to `Q_NOQUOTA`, and on success copies returned quota values into `qres` with `Q_OK`.

State and persistence: it does not persist state directly. Durable state is owned by the FSAL/backend quota implementation. It mutates request-local `op_ctx` by setting the export and depends on the surrounding request cleanup to release it.

Dependencies and integration points: integrates RQUOTA protocol dispatch with export manager lookup, NFS credential extraction, `op_ctx`, FSAL quota operations, and protocol XDR types from `rquota.h`. It assumes the selected export supports `set_quota`.

Risks: path/export lookup failures leave status at `Q_EPERM` but return `NFS_REQ_OK`, so callers receive a protocol-level success with quota-level denial. `rq_curfiles` is not copied from the input or output in this handler even though XDR carries it. Correct authorization depends on `nfs_req_creds()` and the FSAL implementation. The extended protocol accepts arbitrary quota type integers and passes them through.

Test signals: exercise legacy and extended setquota requests, tag/pseudo/path export lookup modes, missing export, credential failure, FSAL success, FSAL `ERR_FSAL_NO_QUOTA`, and backend error cases. Verify result status and all returned quota fields on success.
