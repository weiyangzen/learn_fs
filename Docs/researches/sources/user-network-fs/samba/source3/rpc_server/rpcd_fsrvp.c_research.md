# sources/user-network-fs/samba/source3/rpc_server/rpcd_fsrvp.c

## Purpose
`rpcd_fsrvp.c` wraps the File Server VSS Agent RPC service. It advertises and registers FSRVP only when Samba is not running as an Active Directory DC.

## Important APIs, Types, And Functions
`fsrvp_interfaces` returns `ndr_table_FileServerVssAgent` or zero interfaces on AD DC. `fsrvp_servers` loads shares, returns `FileServerVssAgent_get_ep_server`, or returns an empty server list on AD DC. `main` uses `rpc_worker_main` with five workers and a 60 second idle timeout.

## Control Flow
The callbacks mirror each other: AD DC role short-circuits to no interfaces/servers; other roles load share configuration and register the FSRVP endpoint.

## State And Persistence
The file directly loads share configuration. Any snapshot or VSS state is handled by the endpoint server implementation, not this wrapper.

## Dependencies And Integration Points
It depends on generated FSRVP NDR compatibility and loadparm role/share APIs. It integrates with `rpc_worker.c` and the FSRVP endpoint implementation.

## Risks And Test Signals
Risks include role-gating divergence and share configuration assumptions for snapshot paths. Test signals are `--list-interfaces` in AD DC and file-server roles, startup after share reload, and FSRVP RPC calls against a configured file server.
