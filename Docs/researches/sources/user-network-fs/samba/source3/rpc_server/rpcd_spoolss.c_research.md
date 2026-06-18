# sources/user-network-fs/samba/source3/rpc_server/rpcd_spoolss.c

## Purpose
`rpcd_spoolss.c` wraps the print spooler RPC service. It conditionally advertises SPOOLSS based on `disable spoolss` and initializes printing subsystems before registering the endpoint server.

## Important APIs, Types, And Functions
`spoolss_interfaces` returns `ndr_table_spoolss` unless `lp_disable_spoolss()` is true. `spoolss_servers` initializes secrets, locking, share configuration, printing subsystem state with the global messaging and tevent contexts, resets the mangle cache, and returns `spoolss_get_ep_server`. `main` uses five workers and a 60 second idle timeout.

## Control Flow
List mode hides the interface when spoolss is disabled. Service mode initializes secrets/locking/shares/printing and returns a single endpoint server.

## State And Persistence
This wrapper initializes secrets access, locking state, print queue processing, share configuration, and mangle cache. Print queue persistence is handled by the printing subsystem.

## Dependencies And Integration Points
It depends on generated SPOOLSS NDR, global contexts, share-mode locking, printing queue processing, Samba messaging, secrets, and smbd helpers.

## Risks And Test Signals
Risks include advertising inconsistency when spoolss is disabled after host discovery, printing subsystem initialization failures, and locking dependencies. Test signals are `disable spoolss` interface listing, printer enumeration/open calls, print queue event handling, and startup failure behavior when secrets or locking are unavailable.
