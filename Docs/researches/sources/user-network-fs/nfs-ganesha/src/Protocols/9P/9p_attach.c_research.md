## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_attach.c

Purpose: implements `_9p_attach`, binding a client fid to an export root or requested attach path/tag for 9P2000.L.

APIs and flow: it parses tag, fid, afid, username/aname, and numeric uid, validates fid bounds, resolves the export by tag, pseudo path, or real path, installs it in `op_ctx`, enforces `EXPORT_OPTION_9P` and privileged-port policy, allocates a `_9p_fid`, resolves user credentials by uid or name, looks up the root object, allocates embedded `STATE_TYPE_9P_FID` state, initializes qid fields, and replies with `RATTACH`.

State/dependencies: creates connection-persistent fid state in `req9p->pconn->fids[]`, holds export/object references, records credential/group data, and relies on `export_mgr`, `nfs_exports`, FSAL lookup/root APIs, and `_9p_proto_tools` credential helpers.

Risks/tests: error cleanup must release partially initialized op context, fids, exports, credentials, and object handles. Test attach by tag/path/pseudo, invalid fid, missing export, non-9P export, unprivileged client ports, uid/name credential failure, and root lookup failure.
