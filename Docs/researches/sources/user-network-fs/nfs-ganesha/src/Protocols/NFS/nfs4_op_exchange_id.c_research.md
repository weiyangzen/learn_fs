# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_exchange_id.c

Purpose: implements NFSv4.1 `EXCHANGE_ID`, which maps a client owner/verifier and server role negotiation into an unconfirmed or confirmed clientid response. It also builds the server owner/scope fields required by RFC 5661.

Important APIs and types: uses `EXCHANGE_ID4args`, `EXCHANGE_ID4res`, `client_owner4`, `nfs_client_record_t`, and `nfs_client_id_t`. It uses `get_client_record`, `create_client_id`, `nfs_client_id_insert`, credential comparison through `nfs_compare_clientcred`, lease/state checks through `valid_lease` and `client_id_has_state`, and cleanup through clientid ref helpers. Response memory uses `gsh_malloc` and is released by `nfs4_op_exchange_id_Free`.

Control flow: the handler rejects minorversion 0 and invalid `eia_flags`, checks response room, computes server pNFS role flags from client requests and `nfs_param.nfsv4_param`, then looks up or creates a `client_record` keyed by owner id, pNFS flags, and transport addresses. Under `client_record->cr_mutex` it implements the RFC cases: non-update with existing confirmed record may return the confirmed response, expire a colliding old clientid, or return `NFS4ERR_CLID_INUSE`; update requests require matching verifier, credential, and `op_ctx->client`; update without a confirmed record returns `NFS4ERR_NOENT`. Existing unconfirmed records are removed before creating a new unconfirmed clientid. Successful responses include clientid, create-session sequence, server flags, state protection `SP4_NONE`, major/minor server owner, server scope, and empty impl id.

State and persistence: it creates, updates, expires, or removes in-memory clientid records and initializes v4.1 session list and create-session sequencing. It records incoming verifier and credential state but currently ignores requested state protection beyond metrics. It allocates response strings that must be freed only on success.

Dependencies and integration: integrates with RPC transport address helpers, NFS credentials, pNFS role configuration, SAL metrics, clientid tables, server owner globals `cid_server_owner` and `cid_server_scope`, and virtual-server address scoping.

Risks: this is a high-concurrency identity negotiation point. Bugs can cause duplicate clientids, incorrect trunking/collision behavior, or leaked response buffers. The `eir_flags` field is ORed in multiple paths; it must be initialized by XDR/result allocation. Virtual-server major id sizing must include the address suffix correctly.

Test signals: cover invalid flags, minorversion 0, first exchange, replay with same verifier, client restart with changed verifier, credential collision, update cases 6 to 9, pNFS role negotiation, response-size failure, and memory cleanup of successful responses.
