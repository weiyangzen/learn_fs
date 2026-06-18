# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_Null.c

Purpose: implements the NFSACL NULL procedure. It is a ping/no-op RPC endpoint used for protocol reachability and dispatch validation.

Important APIs/types/functions: exports `nfsacl_Null(nfs_arg_t *, struct svc_req *, nfs_res_t *)` and `nfsacl_Null_Free(nfs_res_t *)`.

Control flow: the handler logs the call on `COMPONENT_NFSPROTO` at full debug and returns `0`, the success convention used by these null handlers. The free routine intentionally does nothing.

State and persistence: no state is read or modified. Arguments, request, and result are ignored.

Dependencies and integration points: includes common NFS core, export, logging, hashtable, and NFSACL headers so it matches the protocol procedure signature expected by `nfs_proto_functions.h`.

Risks and test signals: low behavioral risk, but procedure registration depends on this symbol. Test via an NFSACL NULL RPC and by validating that result cleanup does not attempt to free uninitialized result fields.
