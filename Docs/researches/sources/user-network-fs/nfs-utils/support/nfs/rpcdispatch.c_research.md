# sources/user-network-fs/nfs-utils/support/nfs/rpcdispatch.c

Purpose: generic server-side RPC dispatcher for table-driven RPC program implementations.

Important API: `rpc_dispatch(struct svc_req *rqstp, SVCXPRT *transp, struct rpc_dtable *dtable, int nvers, void *argp, void *resp)`.

Control flow: validates version range, selects a version table, validates procedure number, fetches the dispatch entry, zeros argument/result storage using configured sizes, decodes arguments with `svc_getargs()`, invokes the handler, sends a reply if the handler returns true and `resp` is non-NULL, then frees decoded arguments.

State and persistence: no module state. It mutates caller-provided argument and response buffers.

Dependencies and integration: depends on RPC service APIs, `rpcmisc.h` table definitions, and `xlog`. Used by generated or hand-written RPC daemons to avoid repetitive dispatch boilerplate.

Risks: caller must pass buffers large enough for the selected table entry. The duplicate procedure bounds checks are harmless. Failure of `svc_freeargs()` exits the process with status 2. Handler return convention must be consistent across services.

Test signals: invalid version, invalid proc, NULL function, decode failure, no-response handlers, send failure, and free-args failure path.
