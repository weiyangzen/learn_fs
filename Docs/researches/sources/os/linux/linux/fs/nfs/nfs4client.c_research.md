# File Research: sources/os/linux/linux/fs/nfs/nfs4client.c

This file manages NFSv4 client objects, callback setup, NFSv4.1+ sessions, pNFS data-server clients, server records, referrals, trunking, and server migration updates.

Key client setup:
- `nfs4_alloc_client()` allocates and initializes an `nfs_client`, validates minor version, initializes NFSv4 locks/work/lists/waitqueues, creates the RPC client, derives callback address when needed, and creates idmap state.
- `nfs4_init_client()` initializes minor-version behavior, callback service, and server trunking discovery. If another usable client is found, it preserves clientid state, optionally adds a trunk transport, and returns the existing client.
- `nfs4_free_client()` shuts down NFSv4-specific resources and then frees the generic client.

Callback and session handling:
- `nfs_get_cb_ident_idr()` allocates v4.0 callback identifiers in the network namespace IDR.
- `nfs4_init_callback()` starts the callback service and sets up backchannel support for session clients.
- `nfs41_init_client()` allocates an NFSv4.1+ session and marks the client as session-initializing so callbacks can find it during create-session races.
- `nfs41_shutdown_client()` cleans pending callback copy state, pNFS DS clients, the session, and clientid.

pNFS data server support:
- `nfs4_find_or_create_ds_client()` maintains per-auth-flavor cloned RPC clients for DS I/O.
- `nfs4_shutdown_ds_clients()` tears those DS RPC clients down.
- `nfs4_set_ds_client()` creates or finds a DS `nfs_client` with MDS-derived owner identity, transport options, pNFS flags, and inherited TLS policy when applicable.

Trunking and client matching:
- `nfs4_match_client()` compares RPC ops, minor version, readiness, clientid, and owner-id compatibility, waiting for in-progress client initialization where necessary.
- `nfs41_walk_client_list()` searches for matching clientid/server-owner entries, treating session trunking as a clientid trunking subcase.
- `nfs4_detect_session_trunking()` verifies clientid, server owner major/minor IDs, and server scope before accepting session trunking.
- `nfs4_add_trunk()` adds a compatible transport to an existing client.

Server setup:
- `nfs4_set_client()` binds an `nfs_server` to a client, applies mount-derived transport flags, sets lease-check state, and links sysfs RPC client state.
- `nfs4_init_server()` copies mount context into a new server, selects the initial auth flavor, sets sizes/timeouts/cache parameters, and initializes the RPC client.
- `nfs4_server_common_setup()` allocates the delegation hash, rejects DS-only clients as metadata servers, initializes sessions, probes root filehandle and capabilities, clamps session sizes, inserts server list nodes, and installs destroy handling.
- `nfs4_create_server()` creates ordinary NFSv4 server records.
- `nfs4_create_referral_server()` creates referral server records, trying RDMA when available and otherwise TCP or TCP-TLS based on parent transport security.

Size limiting:
- `nfs4_session_limit_rwsize()` clamps `dtsize`, `rsize`, and `wsize` by negotiated forechannel sizes.
- `nfs4_session_limit_xasize()` clamps get/set/list xattr sizes using NFSv4.2 XDR overhead constants.

Migration:
- `nfs4_update_server()` switches the existing RPC client transport, computes a local client address, removes the server from lists, binds it to a new/updated `nfs_client`, preserves list membership on failure, and reprobes server capabilities after reinsertion.

Risk areas:
- Client matching/trunking is race-sensitive because the shared client list can contain initializing clients.
- Cleanup spans renewd, minor-version shutdown, callback service, idmap pipe state, DS clients, sessions, sysfs, RPC wait queues, and allocated server-owner strings.
- Referral and migration setup must preserve credentials, transport security policy, mount-derived auth/size options, and client owner identity.
