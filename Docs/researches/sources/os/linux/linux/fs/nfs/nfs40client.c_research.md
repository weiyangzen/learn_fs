# File Research: sources/os/linux/linux/fs/nfs/nfs40client.c

## Purpose
Implements NFSv4.0 client initialization, callback path recovery, and server trunking discovery.

## Key Functions
- `nfs40_init_client()` allocates and initializes the NFSv4.0 slot table.
- `nfs40_shutdown_client()` tears down and frees the slot table.
- `nfs40_handle_cb_pathdown()` marks the lease expired and returns delegations after callback path failure.
- `nfs4_schedule_path_down_recovery()` schedules the state manager after callback path recovery setup.
- `nfs40_discover_server_trunking()` sends SETCLIENTID, stores returned clientid/verifier, then walks existing clients to detect same-server trunking.
- `nfs40_walk_client_list()` tests candidate clients with SETCLIENTID_CONFIRM and swaps callback identifiers when an existing client is confirmed as the same server.

## Research Notes
The delicate logic is callback identifier swapping under per-net client lock and using SETCLIENTID_CONFIRM outcomes to distinguish true trunking from coincidental verifier matches.
