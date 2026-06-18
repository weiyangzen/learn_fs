# File Research: sources/os/linux/linux/fs/nfs/pnfs_nfs.c

## Purpose
`pnfs_nfs.c` provides generic helpers for NFS-based pNFS layout drivers, especially file/flexfile-style layouts. It manages data-server commit buckets, commit-array lifetime, generic commit submission, data-server address/cache handling, data-server client connection setup for NFSv3/NFSv4, multipath address decoding, and sync integration.

## Generic Read/Write and Commit Release
- `pnfs_generic_rw_release()` releases the data-server `nfs_client`, then delegates to MDS pgio release ops.
- `pnfs_generic_prepare_to_resend_writes()` fabricates an unstable verifier result so commit release logic retries writes.
- `pnfs_generic_write_commit_done()` delegates completion to MDS commit done ops and may trigger resend.
- `pnfs_generic_commit_release()` runs commit completion, releases lseg and data-server client references, and frees commit data.

## Commit Bucket Model
- `pnfs_commit_array` contains multiple `pnfs_commit_bucket`s, each with written and committing lists, a layout segment ref, and direct verifier state.
- Arrays are associated with a layout segment and linked into both data-server commit info and the lseg’s commit list.
- `pnfs_alloc_commit_array()` allocates flexible bucket storage and initializes all lists.
- `pnfs_add_commit_array()` inserts a new array unless one already exists for the same lseg.
- RCU and refcounts protect commit arrays while scanners iterate.

## Marking, Clearing, Scanning, and Recovering Commits
- `pnfs_layout_mark_request_commit()` places a write request into the correct data-server commit bucket, sets `PG_COMMIT_TO_DS`, increments `nwritten`, and marks the folio unstable.
- If the lseg is invalid or commit array lookup/setup fails, it reschedules the write through generic completion ops.
- `pnfs_generic_clear_request_commit()` removes a request from its commit list, clears `PG_COMMIT_TO_DS`, updates counters, and releases bucket lseg refs when buckets empty.
- `pnfs_generic_scan_commit_lists()` moves requests from written to committing lists across all arrays/buckets up to `max`.
- `pnfs_generic_recover_commit_reqs()` pulls written requests back to a destination list for retry/recovery.
- Empty buckets release their held lseg refs through `pnfs_free_bucket_lseg()`.

## Generic Commit Submission
- `pnfs_generic_commit_pagelist()` mirrors generic `nfs_commit_list` behavior.
- It creates one MDS commit data object for `mds_pages` when present.
- It allocates data-server commit data for each nonempty committing bucket.
- MDS commits use `nfs_initiate_commit()` against the normal NFS client.
- Data-server commits call the layout-driver-provided `initiate_commit()` callback.
- Allocation failure retries affected commits through `nfs_retry_commit()`.

## Data-Server Cache
- Data servers are cached per network namespace in `nfs4_data_server_cache`, protected by `nfs4_data_server_lock`.
- `nfs4_pnfs_ds_add()` either inserts a new `struct nfs4_pnfs_ds` for a multipath address list or returns an existing matching data server with incremented refcount.
- Address matching treats the first list as a subset of the second and compares IPv4/IPv6 address and port, with IPv6 link-local scope-id checks.
- `nfs4_pnfs_ds_put()` removes and destroys a data server when its refcount drops to zero.
- `destroy_ds()` releases the DS client, all decoded addresses, remote string, and the DS object.

## Data-Server Connection Setup
- `nfs4_pnfs_ds_connect()` serializes connection attempts using `NFS4DS_CONNECTING`.
- It waits for in-progress connection, rejects temporarily unavailable deviceids, then dispatches by data-server NFS version.
- NFSv3 DS connection uses a dynamically requested `nfs3_set_ds_client` symbol and can add compatible transports as aliases.
- NFSv4 DS connection uses `nfs4_set_ds_client()`, initializes DS sessions, and can add session-trunked transports.
- For TLS transports, it adjusts transport identity and server name for the trunked address.
- After connection, it validates `ds_clp` and client initialization status, then traces the result.
- `nfs4_pnfs_v3_ds_connect_unload()` releases the dynamically requested v3 connect symbol.

## Multipath Address Decoding
- `nfs4_decode_mp_ds_addr()` decodes one `netid` and universal address from XDR.
- Parses RFC-style address-plus-port strings where the port is encoded as two decimal octets.
- Supports IPv4 and IPv6, including bracketed human-readable IPv6 remote strings.
- Resolves transport identity with `xprt_find_transport_ident()`.
- Returns a populated `nfs4_pnfs_ds_addr` or cleans up all partial allocations on parse failure.

## Sync Integration
- `pnfs_nfs_generic_sync()` first commits unstable writes with `nfs_commit_inode(..., FLUSH_SYNC)`.
- If the sync is not datasync, it then sends `pnfs_layoutcommit_inode()` to commit layout metadata.
- This is the generic sync behavior for NFS-based pNFS layout drivers.

## Integration Points
- Provides exported helpers used by pNFS layout drivers through declarations in `pnfs.h`.
- Relies on generic NFS commit helpers, RPC transport helpers, NFSv3/NFSv4 DS client setup, NFS net namespace state, and pNFS layout segment validity.
- Bridges layout-driver commit grouping to core NFS commit scheduling.

## Invariants and Risks
- Commit list manipulation assumes `NFS_I(inode)->commit_mutex` is held for paths that modify request lists.
- Commit arrays are RCU-visible; removal must use RCU-safe deletion and refcount checks.
- Bucket lseg references are transferred between written/committing lists and commit data; leaks or premature puts would corrupt layoutcommit/commit retry behavior.
- DS connection serialization prevents duplicate client setup, but callers must still handle temporary device unavailability and incomplete client initialization.
- Address subset matching can intentionally coalesce multipath representations, so layout drivers should supply stable address lists.
