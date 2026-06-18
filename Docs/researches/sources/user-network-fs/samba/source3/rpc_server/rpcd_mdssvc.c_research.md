# sources/user-network-fs/samba/source3/rpc_server/rpcd_mdssvc.c

## Purpose
`rpcd_mdssvc.c` wraps the Spotlight metadata service RPC endpoint for source3.

## Important APIs, Types, And Functions
`mdssvc_interfaces` returns `ndr_table_mdssvc`. `mdssvc_servers` loads shares, initializes POSIX locking with `posix_locking_init(false)`, resets the mangle cache, and returns `mdssvc_get_ep_server`. `main` runs through `rpc_worker_main` with five workers and 60 second idle timeout.

## Control Flow
List mode reports the metadata interface. Worker mode initializes filesystem/share support before endpoint server registration.

## State And Persistence
The wrapper initializes share configuration, POSIX locking runtime state, and mangle cache. Metadata indexes or search state are not managed here.

## Dependencies And Integration Points
It depends on source3 locking and smbd helper prototypes plus generated MDSSVC NDR compatibility. It integrates with the metadata endpoint implementation and Samba share configuration.

## Risks And Test Signals
Risks include startup failure if POSIX locking cannot initialize and stale share state. Test signals are interface listing, startup with shares loaded, and Spotlight/MDSSVC RPC calls against shares.
