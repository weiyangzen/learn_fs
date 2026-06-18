# sources/user-network-fs/samba/source3/rpc_server/rpcd_witness.c

## Purpose
`rpcd_witness.c` wraps the SMB witness RPC service used for clustered deployments. It only advertises and registers the witness endpoint when clustering is enabled.

## Important APIs, Types, And Functions
`witness_interfaces` returns `ndr_table_witness` when `lp_clustering()` is true. `witness_servers` registers NTLMSSP and SPNEGO principals of the form `cifs/<netbios name>`, optionally registers KRB5 in ADS security mode, sets the dcesrv preferred transfer syntax to NDR64, and returns `witness_get_ep_server`. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List and service callbacks short-circuit to empty results when clustering is disabled. With clustering enabled, service setup performs auth-principal registration, chooses NDR64 preference, and returns one endpoint server.

## State And Persistence
The wrapper mutates runtime dcesrv auth registrations and preferred transfer syntax. Cluster state and witness registrations are handled by the endpoint implementation.

## Dependencies And Integration Points
It depends on generated witness NDR compatibility, clustering and security loadparm settings, NetBIOS name, and dcesrv auth registration. It integrates with SMB clustered failover client notification flows.

## Risks And Test Signals
Risks include principal construction mismatch, missing KRB5 registration in ADS deployments, and NDR64 negotiation assumptions. Test signals are clustering on/off interface listing, auth negotiation for NTLMSSP/SPNEGO/KRB5, NDR64 bind preference, and witness subscription calls in clustered test environments.
