# sources/user-network-fs/samba/source3/utils/net_util.c

## Purpose
Shared helper layer for `net`: RPC name lookup, service/IPC connection setup, server discovery, machine-account credential selection, subcommand dispatch, usage rendering, share type labels, and DC scanning.

## Important APIs, Types, and Functions
`net_rpc_lookup_name()` opens LSA over an existing `cli_state`. `connect_to_service()`, `connect_to_ipc()`, and `connect_to_ipc_anonymous()` wrap `cli_full_connection_creds()`. `connect_dst_pipe()` opens a destination RPC pipe. `net_use_krb_machine_account()` configures credentials from `secrets.tdb`. `net_find_server()` resolves explicit host/IP, PDC, DMB, master browser, or localhost. `net_make_ipc_connection_ex()` connects and stores PDC affinity. `net_run_function()` dispatches function tables. `net_scan_dc()` uses DSSETUP with LSA fallback.

## Control Flow
Callers discover and connect through `net_make_ipc_connection_ex()`, which resolves a server, connects anonymously or with credentials, stores affinity for PDCs, and applies request timeout. Command modules pass `functable` arrays to `net_run_function()`. DC scanning first tries DSSETUP and falls back to LSA account-domain info.

## State and Persistence
Mostly transient network state. Machine-account setup reads secrets and mutates in-memory credentials. PDC connections may update the server affinity cache.

## Dependencies and Integration Points
Central glue for many `net_*` modules, depending on libsmb transport, NetBIOS lookup, RPC pipe clients, generated LSA/DSSETUP stubs, credentials/gensec, loadparm, secrets, and netlogon warning helpers.

## Risks
Server discovery can unexpectedly default to localhost unless flags prevent it. Machine-account setup exits on secrets initialization failure. Different discovery flags materially change the contacted server.

## Test Signals
Cover dispatch/usage, explicit host/IP, PDC/master/localhost discovery, anonymous vs authenticated IPC, timeout propagation, affinity storage, LSA/DSSETUP scan fallback, machine credentials, and credential-specific connection errors.
