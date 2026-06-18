# sources/user-network-fs/samba/source4/ntvfs/ntvfs_interface.c

Purpose: provides the public NTVFS dispatch wrappers and module-stack pass-through wrappers. It is intentionally thin glue between callers and `struct ntvfs_ops`.

Important APIs and functions: top-level wrappers such as `ntvfs_connect`, `ntvfs_open`, `ntvfs_read`, `ntvfs_write`, `ntvfs_trans`, `ntvfs_notify`, and `ntvfs_cancel` dispatch to `req->ctx->modules`. `ntvfs_next_*` variants dispatch to `ntvfs->next` for stacked modules. Address and oplock helpers are `ntvfs_set_addresses`, `ntvfs_get_local_address`, `ntvfs_get_remote_address`, `ntvfs_set_oplock_handler`, and `ntvfs_send_oplock_break`.

Control flow: each wrapper checks whether the target module and operation callback exist, returns `NT_STATUS_NOT_IMPLEMENTED` if absent, and otherwise calls the callback with the module context, request, and operation union. `ntvfs_disconnect` also validates a non-null context. Pass-through functions are mechanically parallel to top-level wrappers but advance one module down the linked list.

State and persistence: this file stores copied local/remote socket addresses under the NTVFS context and installs an oplock callback pointer/private data. It otherwise persists no filesystem data and does not own backend state.

Dependencies and integration points: integrates frontends with backend modules and stacked filters. Uses tsocket address copying and the oplock callback stored in `struct ntvfs_context`.

Risks: the wrappers assume `req`, `ctx`, and the first module are valid; missing callbacks surface as `NOT_IMPLEMENTED`; stacked modules must choose top-level versus `next` dispatch correctly or may recurse or bypass filters. Test signals include every operation returning `NOT_IMPLEMENTED` when absent, pass-through to next module, address copy lifetime, oplock break callback invocation, and invalid-context disconnect handling.
