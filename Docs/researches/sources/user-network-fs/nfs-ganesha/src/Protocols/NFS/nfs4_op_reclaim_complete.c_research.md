# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_reclaim_complete.c

## Purpose
Implements NFSv4.1 `RECLAIM_COMPLETE`, letting a session client signal that reboot reclaim for the client is complete. It updates client recovery flags and notifies the state layer.

## Important APIs, Types, and Functions
- `nfs4_op_reclaim_complete` handles the operation.
- Uses `data->session->clientid_record` and its `cid_cb.v41.cid_reclaim_complete` flag.
- Calls `nfs41_reclaim_complete_clid` and increments global `reclaim_completes` when reclaim was allowed.
- `nfs4_op_reclaim_complete_Free` is a no-op.

## Control Flow
The handler sets `resp->resop` and initializes success. If the request is for all filesystems and the client already completed reclaim, it returns `NFS4ERR_COMPLETE_ALREADY`. If `rca_one_fs` is false, it marks the client complete, increments the reclaim-complete counter when applicable, and calls the SAL recovery completion helper. One-filesystem completion is accepted but currently does not update per-filesystem state.

## State and Persistence Behavior
Mutates in-memory client recovery state. It may affect server-wide recovery progress via `reclaim_completes` and the SAL reclaim-complete callback. It does not write persistent recovery records directly in this file.

## Dependencies and Integration Points
Requires an established NFSv4.1 session in `compound_data_t`. Integrates with SAL client/recovery structures and LTTng tracepoints.

## Risks
The implementation explicitly does not handle `rca_one_fs` beyond accepting it, so per-filesystem recovery semantics may be incomplete. Duplicate all-filesystem completion must return `COMPLETE_ALREADY` without re-notifying recovery state.

## Test Signals
Test first all-filesystem completion, duplicate completion, `rca_one_fs` behavior, clients with and without `cid_allow_reclaim`, and behavior when invoked in a valid v4.1 session after server grace/recovery.
