# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs_nfs.c

This file provides generic helpers for pNFS file-based layout drivers. It covers data-server commit bucket management, pNFS commit dispatch, data-server address caching, NFSv3/NFSv4 data-server connection setup, multipath DS address decoding, and generic sync behavior.

Generic read/write and commit release helpers:
- `pnfs_generic_rw_release()` releases a referenced DS `nfs_client` and then delegates to the MDS RPC release op stored in the pgio header.
- `pnfs_generic_prepare_to_resend_writes()` fabricates an unstable write verifier result so normal commit release logic retries writes.
- `pnfs_generic_write_commit_done()` delegates commit completion to the MDS call-done path.
- `pnfs_generic_commit_release()` runs commit completion, drops the layout segment, drops the DS client, and releases commit data.

Commit bucket model:
- `pnfs_commit_array` owns one or more `pnfs_commit_bucket` entries for a specific layout segment.
- Each bucket has `written` and `committing` lists, an lseg reference, and a direct verifier.
- Non-empty buckets hold an lseg reference so commit state remains valid while requests are waiting or committing.
- `pnfs_alloc_commit_array()` and `pnfs_free_commit_array()` allocate/free bucket arrays, with RCU freeing.
- `pnfs_add_commit_array()` attaches a new array to `pnfs_ds_commit_info` and the lseg’s `pls_commits` list unless one already exists for that lseg.
- `pnfs_generic_ds_cinfo_release_lseg()` and `pnfs_generic_ds_cinfo_destroy()` remove arrays associated with one lseg or all DS commit info.

Commit request list operations:
- `pnfs_generic_clear_request_commit()` removes a request from DS commit tracking, clears `PG_COMMIT_TO_DS`, decrements written count, and drops the bucket lseg if the bucket becomes empty.
- `pnfs_generic_scan_commit_lists()` scans per-DS written lists into committing lists, updating `nwritten` and `ncommitting`.
- `pnfs_generic_recover_commit_reqs()` recovers pending written requests into a destination list, used when DS commit state must fall back or be retried.
- `pnfs_generic_commit_pagelist()` builds commit calls for both MDS commit pages and DS commit buckets. MDS pages are committed through normal `nfs_initiate_commit()`, while DS buckets are dispatched through a layout-driver-provided `initiate_commit()` callback.
- Error during DS commit allocation causes remaining committing requests to be retried through `nfs_retry_commit()`.

Data-server cache:
- Data servers are cached per network namespace in `nfs_net->nfs4_data_server_cache`.
- `nfs4_pnfs_ds_add()` either creates a new `nfs4_pnfs_ds` from a list of multipath addresses or finds an existing DS whose cached addresses cover the supplied list. It increments the DS refcount on reuse.
- Address matching supports IPv4 and IPv6, including link-local IPv6 scope-id checks.
- `nfs4_pnfs_ds_put()` removes and destroys a DS when its refcount reaches zero.
- `destroy_ds()` drops the DS client, frees all DS addresses, debug remote strings, and the DS object.

Data-server connection setup:
- `nfs4_pnfs_ds_connect()` serializes connection attempts with `NFS4DS_CONNECTING`, checks device unavailability, dispatches by DS NFS version, clears the connect bit, validates `ds_clp`, and traces the result.
- `_nfs4_pnfs_v3_ds_connect()` lazily loads `nfs3_set_ds_client`, tries each DS address, creates or aliases transports, honors TLS transport policy from the MDS client, and disables soft retry behavior on the DS RPC client.
- `_nfs4_pnfs_v4_ds_connect()` creates NFSv4 DS clients, initializes DS sessions, and can add trunked transports using the client’s session-trunking callback.
- TLS trunking paths build an address-derived server name for the DS transport when needed.
- `nfs4_pnfs_v3_ds_connect_unload()` releases the optional NFSv3 DS connect symbol.

Multipath DS address decoding:
- `nfs4_decode_mp_ds_addr()` decodes RFC 5665 netid and universal-address strings from XDR.
- It splits the final two decimal octets into a TCP/UDP port, parses IPv4/IPv6 addresses with `rpc_pton()`, maps netid to transport with `xprt_find_transport_ident()`, records address length, and creates a printable `host:port` or `[ipv6]:port` string.
- Unsupported address families, malformed strings, or unknown netids fail cleanly and free intermediate allocations.

Request commit marking:
- `pnfs_layout_mark_request_commit()` finds or creates the commit array for an lseg, validates that the lseg is still valid, assigns the request to a DS commit bucket, sets `PG_COMMIT_TO_DS`, increments `nwritten`, adds the request to the commit list under `commit_mutex`, and marks the folio unstable.
- If no valid DS commit bucket is available, it reschedules the write through the completion ops.

Sync:
- `pnfs_nfs_generic_sync()` first commits outstanding writes with `nfs_commit_inode(..., FLUSH_SYNC)`. For full fsync, it then sends synchronous `pnfs_layoutcommit_inode()`; for datasync it stops after the commit.

Concurrency:
- DS cache updates use `nfs4_data_server_lock`.
- Commit array lookup uses RCU plus array refcounts; list mutation uses inode `commit_mutex` and, for array release, inode `i_lock`.
- DS connection setup uses a bit lock/wait on `NFS4DS_CONNECTING` so only one task initializes `ds_clp`.
- Memory ordering around `WRITE_ONCE(ds->ds_clp, clp)` ensures connected clients become visible after initialization.
