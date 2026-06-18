# sources/user-network-fs/samba/source3/rpc_server/rpcd_classic.c

## Purpose
`rpcd_classic.c` defines a worker daemon for traditional source3 administrative RPC interfaces: SRVSVC, DFS, INITSHUTDOWN, SVCCTL, NTSVCS, EVENTLOG, and WKSSVC.

## Important APIs, Types, And Functions
`classic_interfaces` returns the NDR tables. `classic_servers` builds the matching endpoint server array with `*_get_ep_server` calls, initializes secrets, locking, share info, share-loaded configuration, mangle cache, and default machine-principal auth types. `main` runs `rpc_worker_main` with daemon config name `rpcd_classic`, five default workers, and 60 second idle timeout.

## Control Flow
List mode only reports the static interface list through `classic_interfaces`. Service mode performs required source3 state initialization before returning endpoint servers for registration by `rpc_worker.c`.

## State And Persistence
State initialized here includes secrets database access, locking database state, share info database state, loaded shares, and mangle cache. Persistent updates are delegated to those subsystems, not directly written here.

## Dependencies And Integration Points
It depends on generated NDR server compatibility headers, source3 secrets, share-mode locking, and smbd share/mangle helpers. It integrates with the generic worker and source3 administrative endpoint implementations.

## Risks And Test Signals
Risks include initialization order, failure paths that call `exit(1)` inside the callback, and stale share configuration without reload. Test signals are `rpcd_classic --list-interfaces`, startup with secrets/locking/share db available, and RPC smoke tests for srvsvc, dfs, svcctl, eventlog, and wkssvc.
