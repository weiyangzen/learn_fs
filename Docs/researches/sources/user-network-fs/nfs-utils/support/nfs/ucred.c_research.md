# sources/user-network-fs/nfs-utils/support/nfs/ucred.c

Purpose: construct `struct nfs_ucred` values from RPC request authentication credentials and export squash policy.

Important API: `int nfs_ucred_get(struct nfs_ucred **credp, struct svc_req *rqst, const struct exportent *ep)`. Internal helpers initialize credentials from AUTH_UNIX, RPCSEC_GSS, AUTH_DES, or anonymous/null fallback.

Control flow: request auth flavor selects initialization path. AUTH_UNIX copies `authunix_parms`. RPCSEC_GSS calls `rpc_gss_getcred()` when available. AUTH_DES calls `authdes_getucred()` when available. Unknown flavors become anonymous credentials. `nfs_ucred_init_cred()` applies all-squash, root-squash, and root-group squash rules before returning the heap-allocated credential.

State and persistence: allocates a credential and optional group list for the caller to own/free. No persistent state.

Dependencies and integration: depends on RPC request structs, optional tirpc GSS/DES APIs, export flags, and shared `nfs_ucred` helpers from misc. Used by NFS service code needing filesystem credentials corresponding to an RPC caller.

Risks: group arrays are heap allocated and require consistent freeing by callers. Root-squash preserves nonzero primary GID when UID is 0, while group list is anonymous/empty; tests should confirm this matches policy. Unsupported auth flavors silently map to anonymous.

Test signals: AUTH_UNIX user/group/groups, all-squash, root-squash uid 0 with gid 0 and nonzero gid, RPCSEC_GSS success/failure, AUTH_DES success/failure, unknown auth flavor, and allocation failure.
