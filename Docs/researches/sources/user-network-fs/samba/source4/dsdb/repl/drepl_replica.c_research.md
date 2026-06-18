# sources/user-network-fs/samba/source4/dsdb/repl/drepl_replica.c

Purpose: placeholder handlers for forwarded `DsReplicaAdd`, `DsReplicaDel`, and `DsReplicaMod` requests.

Important APIs/functions: `drepl_replica_add()`, `drepl_replica_del()`, and `drepl_replica_mod()` log the incoming DRSUAPI request with `NDR_PRINT_FUNCTION_DEBUG()` and return `NT_STATUS_NOT_IMPLEMENTED`.

Control flow/state: no mutation is performed. These functions are called by IRPC wrappers in `drepl_service.c`, but the implementation stops at debug tracing.

Dependencies/integration: DRSUAPI generated structures, DREPL service type, Samba debug/NDR helpers, and IRPC registration through `drepl_service.c`. Risks are primarily feature gaps: callers expecting Add/Del/Mod topology management will receive not implemented despite the service registering handlers. Test signals: RPC/IRPC callers should see `NT_STATUS_NOT_IMPLEMENTED`; debug output should include the inbound request for diagnosis; no DSDB state should change.
