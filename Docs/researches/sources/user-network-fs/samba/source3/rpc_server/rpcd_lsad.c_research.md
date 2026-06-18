# sources/user-network-fs/samba/source3/rpc_server/rpcd_lsad.c

## Purpose
This daemon wrapper provides LSA, SAMR, DSSETUP, and conditionally NETLOGON through source3. It adapts the advertised interfaces and endpoint servers to Samba server role.

## Important APIs, Types, And Functions
`lsad_interfaces` returns LSARPC, SAMR, DSSETUP, and maybe NETLOGON. Standalone and member roles drop NETLOGON, while AD DC returns no interfaces because source4 provides these services. `lsad_servers` builds matching endpoint servers, initializes secrets, registers default machine-principal auth types, and for classic DC roles registers schannel with an empty principal. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List and service callbacks apply the same role logic. Service initialization occurs before role-specific server count adjustment so secrets and auth registration are available for source3 roles.

## State And Persistence
The wrapper initializes secrets access and runtime auth registrations. Persistent account, SAM, LSA, and netlogon state is owned by endpoint implementations and passdb/secrets.

## Dependencies And Integration Points
It depends on generated NDR compatibility for LSA, SAMR, NETLOGON, DSSETUP, source3 auth, and secrets. It is a major provider for authentication and account-management RPC in non-AD-DC source3 deployments.

## Risks And Test Signals
Risks include incorrect role gating, schannel principal registration, and source4/source3 service overlap on AD DC. Test signals are role-specific interface listing, SAMR password operations, LSA policy calls, netlogon availability only for classic DC roles, and auth type negotiation.
