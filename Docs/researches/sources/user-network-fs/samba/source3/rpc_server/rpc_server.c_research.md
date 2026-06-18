# sources/user-network-fs/samba/source3/rpc_server/rpc_server.c

## Purpose
This file implements generic source3 DCE/RPC server support shared by embedded and worker-based transports. It prepares GENSEC authentication, logs successful authorization, manages association groups, resolves named-pipe endpoints, and terminates ncacn transport connections.

## Important APIs, Types, And Functions
`dcesrv_auth_gensec_prepare` builds a `gensec_security` context for a call. `dcesrv_log_successful_authz` emits audit events after authorization. `dcesrv_assoc_group_new`, `dcesrv_assoc_group_reference`, and `dcesrv_assoc_group_find` manage association group IDs in `dce_ctx->assoc_groups_idr`. `dcesrv_transport_terminate_connection` and `ncacn_terminate_connection` free the ncacn connection object. `dcesrv_endpoint_by_ncacn_np_name` finds a named-pipe endpoint by pipe name. `dcesrv_get_pipes_struct` extracts the source3 `pipes_struct` from a `dcesrv_connection`.

## Control Flow
During bind handling, dcesrv calls the configured auth callback to prepare GENSEC, then association-group callback to either reference a requested group or allocate a new random ID. On successful authorization, audit logging constructs an auth4 context under root and records remote/local addresses, service, auth type, transport protection, and session info. Named-pipe endpoint lookup iterates the endpoint list, filters to `NCACN_NP`, strips a leading `\pipe\`, and compares names.

## State And Persistence
Association groups are runtime talloc objects registered in an IDR and removed by `dcesrv_assoc_group_destructor`. Audit logging persists through Samba's configured authz log path. No configuration is mutated.

## Dependencies And Integration Points
Dependencies include `dcesrv_core`, `rpc_pipes.h`, `rpc_config.h`, `rpc_dce.h`, generated auth/netlogon NDR headers, tsocket, named-pipe auth, source3 auth, and random ID allocation. Worker mode overrides association-group handling in `rpc_worker.c`, but still reuses auth preparation, authz logging, endpoint lookup, and transport termination.

## Risks And Test Signals
Risks include association group ID exhaustion, transport mismatch on reused groups, audit logging failures under memory pressure, and ambiguous named-pipe names if endpoint strings vary in slash or case normalization. Test signals are bind with new and existing association groups, cross-transport group reuse rejection, successful-authz audit records, named-pipe endpoint lookup with and without `\pipe\`, and connection termination callbacks.
