# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_session.c

Purpose: implements `NFS4_OP_DESTROY_SESSION`, the NFSv4.1 operation that deletes an established session. The public functions are `nfs4_op_destroy_session` and a no-op `nfs4_op_destroy_session_Free`.

Important APIs and types: uses `DESTROY_SESSION4args`, `DESTROY_SESSION4res`, and `nfs41_session_t`. It depends on `nfs41_Session_Get_Pointer`, `check_session_conn`, `nfs41_Session_Del`, and `dec_session_ref`.

Control flow: the handler rejects NFSv4.0 compounds with `NFS4ERR_INVAL`. It resolves the supplied session id into a session pointer; failure maps to `NFS4ERR_BADSESSION`. It then enforces RFC behavior that `DESTROY_SESSION` be invoked over a connection associated with that session via `check_session_conn(session, data, false)`, returning `NFS4ERR_CONN_NOT_BOUND_TO_SESSION` if not. A successful connection check calls `nfs41_Session_Del`; delete failure is converted to `NFS4ERR_BADSESSION`, otherwise the operation completes with `NFS4_OK`.

State and persistence: the operation removes the session from the in-memory NFSv4.1 session registry. It does not directly remove clientids, stable recovery records, open state, or locks. Reference ownership is simple: the lookup takes a session reference and every path after lookup drops it.

Dependencies and integration: tightly integrated with session-table SAL code, connection binding checks, NFS QoS/session request handling, and LTTng NFSv4 tracepoints. It returns through `nfsstat4_to_nfs_req_result` for compound control.

Risks: the primary risk is accepting a request on the wrong transport, which would violate session-channel binding; `check_session_conn` is the guard. Race risk is limited to deletion after lookup; `nfs41_Session_Del` must be idempotent enough to report `BADSESSION`. Cleanup must always release the lookup reference.

Test signals: exercise minorversion 0 rejection, unknown session ids, connection-not-bound failure, successful delete, and duplicate destroy after a successful delete.
