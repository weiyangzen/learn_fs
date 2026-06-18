# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40client.c

## Purpose
Implements NFSv4.0 client initialization, shutdown, callback-path recovery, and v4.0 server trunking discovery.

## Client Slot Table
- `nfs40_init_client(struct nfs_client *clp)`
  - Allocates a v4.0 slot table.
  - Initializes it with `NFS4_MAX_SLOT_TABLE`.
  - Stores it in `clp->cl_slot_tbl`.
- `nfs40_shutdown_client(struct nfs_client *clp)`
  - Shuts down and frees the slot table if present.

## Callback Path Recovery
- `nfs40_handle_cb_pathdown(struct nfs_client *clp)`
  - Sets `NFS4CLNT_LEASE_EXPIRED`.
  - Expires all delegations to force callback path recovery.
- `nfs4_schedule_path_down_recovery(struct nfs_client *clp)`
  - Invokes v4.0 callback pathdown handling and schedules the state manager.

## Callback Ident Swapping
- `nfs4_swap_callback_idents(struct nfs_client *keep, struct nfs_client *drop)`
  - Used when trunking discovery proves two clients are the same server after SETCLIENTID changed callback identity.
  - Swaps IDR entries and `cl_cb_ident` values under the namespace NFS client lock.

## Server Trunking Discovery
- `nfs4_same_verifier()` compares v4 verifiers.
- `nfs40_walk_client_list()`
  - Walks the per-net client list looking for an existing client matching the new one.
  - Uses `nfs4_match_client()` and `SETCLIENTID_CONFIRM` to prove sameness.
  - Handles stale clientid, restart/timeout callback path recovery, and callback ident swap.
  - Returns a referenced matching client through `result` on success.
- `nfs40_discover_server_trunking()`
  - Sends `SETCLIENTID` with callback port for IPv4 or IPv6.
  - Stores returned clientid/confirm verifier.
  - Calls `nfs40_walk_client_list()`.
  - On success, schedules state renewal for the matched client and state manager if needed.

## Research Notes
This is v4.0-specific because NFSv4.0 trunking and callback setup use SETCLIENTID/SETCLIENTID_CONFIRM rather than the v4.1+ session model.
