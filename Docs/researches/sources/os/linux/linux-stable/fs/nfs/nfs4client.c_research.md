# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4client.c

This file manages NFSv4 client objects, callback setup, sessions, pNFS data-server clients, server records, referrals, trunking, and server migration updates.

Key client setup:
- `nfs4_alloc_client()` allocates and initializes an `nfs_client`.
  - Validates minor version.
  - Initializes locks, renewal work, data-server list, wait queues, migration generation, pending callback stateids.
  - Creates RPC client, derives callback IP address if needed, and creates idmap state.
- `nfs4_init_client()` initializes minor-version behavior, callback service, and server trunking discovery.
- `nfs4_free_client()` shuts down NFSv4-specific resources then frees the generic client.

Callback and session handling:
- `nfs_get_cb_ident_idr()` allocates v4.0 callback identifiers.
- `nfs4_init_callback()` starts callback service and sets up backchannel for sessions.
- `nfs41_init_client()` allocates an NFSv4.1+ session and marks the client as session-initializing.
- `nfs41_shutdown_client()` cleans callback copy state, pNFS DS clients, session, and clientid.

pNFS data server support:
- `nfs4_find_or_create_ds_client()` clones per-auth-flavor RPC clients for DS I/O.
- `nfs4_shutdown_ds_clients()` tears those clients down.
- `nfs4_set_ds_client()` creates or finds a DS `nfs_client` with MDS-derived identity, transport parameters, and pNFS flags.
- TLS policy may be inherited from MDS if available.

Trunking and client matching:
- `nfs4_match_client()` checks version, minor version, readiness, clientid, and owner-id compatibility.
- `nfs41_walk_client_list()` searches for matching clientid/server-owner entries.
- `nfs4_detect_session_trunking()` verifies clientid, server owner major/minor IDs, and server scope before accepting session trunking.
- `nfs4_add_trunk()` adds a transport to an existing client when trunking succeeds.

Server setup:
- `nfs4_set_client()` binds an `nfs_server` to a client, sets init flags, handles transport constraints, and sysfs linkage.
- `nfs4_init_server()` copies mount context into a new server and initializes RPC client flavor.
- `nfs4_server_common_setup()` allocates delegation hash, initializes session, probes root filehandle, probes server capabilities, applies session size limits, inserts server into lists, and installs destroy callback.
- `nfs4_create_server()` creates normal NFSv4 server records.
- `nfs4_create_referral_server()` creates referral server records, trying RDMA then TCP/TLS paths.

Size limiting:
- `nfs4_session_limit_rwsize()` clamps `dtsize`, `rsize`, and `wsize` by negotiated forechannel sizes.
- `nfs4_session_limit_xasize()` clamps get/set/list xattr sizes using v4.2 overhead constants.

Migration:
- `nfs4_update_server()` switches RPC transport, computes local client address, replaces the client association, preserves list membership, and reprobes the server.

Risk areas:
- Client matching/trunking is sensitive to initialization races; `nfs4_match_client()` can wait for another client to finish initialization while walking the shared list.
- Resource cleanup spans callback, idmap, sessions, DS clients, sysfs, and RPC wait queues.
- Referral and migration setup must preserve credentials, transport security policy, and mount-derived size/security options.
