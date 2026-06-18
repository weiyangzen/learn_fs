<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c

## Purpose
Implements NFSv4.1 `OP_BIND_CONN_TO_SESSION`, associating the current transport connection with an existing session forechannel and optionally establishing backchannel use.

## APIs, Types, and Functions
Important functions are `nfs4_op_bind_conn()`, `bind_conn_to_session_backchannel()`, and `nfs4_op_nfs4_op_bind_conn_Free()`. It uses `BIND_CONN_TO_SESSION4args/res`, `nfs41_Session_Get_Pointer()`, `reserve_lease_or_expire()`, `check_session_conn()`, `nfs_rpc_create_chan_v41()`, `display_session_id()`, `display_xprt_sockaddr()`, `inc_client_id_ref()`, and `dec_session_ref()`.

## Control Flow, State, and Persistence
The handler rejects minor version 0, looks up the session, reserves the client lease, stores the session and preserved clientid in compound data, adds the current transport to the session connection list, echoes the session ID, and maps the client-requested channel direction. Backchannel requests call `bind_conn_to_session_backchannel()`, which supports only `SP4_NONE` and creates the RPC callback channel. Optional backchannel failure for `FORE_OR_BOTH` degrades to forechannel-only; mandatory failures return errors. Success updates `op_ctx->clientid` and returns selected server channel direction. Persistent state includes session connection membership and possible backchannel resources.

## Dependencies and Integration
Depends on session/clientid tables, lease management, transport state, callback RPC channel creation, and compound cleanup to release preserved references. `nfs4_Compound.c` also enforces that this op is single/first-position as required.

## Risks and Test Signals
Risks include leaked session/clientid refs on mid-handler errors, duplicate or stale connection records, unsupported state protection modes, backchannel setup failures, and RDMA mode echo semantics. Test signals are bind forechannel-only, mandatory and optional backchannel binds, bad session, expired lease, v4.0 invalid use, compound position errors, duplicate connection handling, and connection teardown cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c -->
