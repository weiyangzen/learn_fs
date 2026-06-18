# sources/user-network-fs/samba/source3/rpc_server/rpcd_rpcecho.c

## Purpose
This daemon wrapper exposes the test/diagnostic RPCECHO interface outside AD DC mode.

## Important APIs, Types, And Functions
`rpcecho_interfaces` returns `ndr_table_rpcecho` unless the role is AD DC. `rpcecho_servers` returns `rpcecho_get_ep_server` unless AD DC. `main` uses one worker and a one second idle timeout through `rpc_worker_main`.

## Control Flow
The wrapper mirrors source4 ownership rules for AD DC. In non-AD DC roles it advertises and registers the echo endpoint; on AD DC it reports no interfaces or servers.

## State And Persistence
No persistent state is owned. The service is mainly diagnostic and keeps only worker runtime state.

## Dependencies And Integration Points
It depends on generated echo NDR compatibility, loadparm role detection, and `rpc_worker_main`.

## Risks And Test Signals
Risks are low but include accidental exposure in AD DC mode and idle timeout churn during tests. Test signals are role-specific `--list-interfaces`, basic echo RPC calls, and worker idle shutdown.
