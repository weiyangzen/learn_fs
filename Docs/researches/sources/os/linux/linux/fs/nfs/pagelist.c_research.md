# File Research: sources/os/linux/linux/fs/nfs/pagelist.c

## Purpose
`pagelist.c` implements generic NFS read/write request management. It allocates `struct nfs_page` requests, groups and splits them, coalesces contiguous requests into larger pgio RPCs, manages mirrored pageio descriptors, initiates RPC or localio pgio calls, and handles resend/error cleanup.

## Request Lifetime
- Uses `nfs_page_cachep`, initialized by `nfs_init_nfspagecache()` and destroyed by `nfs_destroy_nfspagecache()`, to allocate `struct nfs_page`.
- `nfs_page_create_from_page()` and `nfs_page_create_from_folio()` create head requests from locked page/folio input.
- `nfs_create_subreq()` splits an existing request into subrequests that share the same page group.
- Request cleanup releases page/folio references, lock contexts, open-context-derived I/O counters, and wakes waiters.
- `nfs_release_request()` uses a `kref` callback that coordinates page-group teardown so all grouped requests are freed together when safe.

## Page Group Synchronization
- `PG_HEADLOCK` protects request group traversal and modification.
- `nfs_page_group_lock()` locks both the request and head when needed; `nfs_page_group_unlock()` releases in reverse.
- `nfs_page_group_sync_on_bit_locked()` lets all requests in a group rendezvous on a `PG_*` bit, then clears the bit across the group.
- Teardown uses `PG_TEARDOWN` to ensure subrequests do not free shared group state prematurely.

## Coalescing and Splitting
- `nfs_generic_pg_test()` enforces block-size and page-array-size limits.
- `nfs_coalesce_size()` additionally requires matching open contexts, compatible lock owners when POSIX/flock locks exist, and contiguous page/folio/file offsets.
- `__nfs_pageio_add_request()` adds a request to the active descriptor or splits it into subrequests when only part of the request can fit.
- When coalescing fails because the current batch is full, the code submits current I/O, then retries the request.
- `nfs_do_recoalesce()` handles layout-driver or mirror-triggered recoalescing by rebuilding descriptor lists.

## Pageio Descriptor and Mirroring
- `nfs_pageio_init()` initializes an `nfs_pageio_descriptor` with operation tables, completion ops, rw ops, block size, and one static mirror.
- Mirror count can be changed by `pg_get_mirror_count`; dynamic mirrors are allocated up to `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`.
- `nfs_pgio_current_mirror()` and layout-driver hooks select the active mirror.
- `nfs_pageio_complete()` drains each mirror, runs error cleanup, calls optional `pg_cleanup`, and frees dynamic mirror storage.
- `nfs_pageio_stop_mirroring()` completes outstanding I/O, reducing operation back to normal non-mirrored behavior.

## RPC Setup and Dispatch
- `nfs_pgheader_init()` builds `struct nfs_pgio_header` from a descriptor and current mirror.
- `nfs_generic_pgio()` moves requests from the descriptor to the header, builds the page vector, sets stable-write behavior, initializes commit info, and fills RPC args/results.
- `nfs_generic_pg_pgios()` allocates a header, prepares pgio, optionally opens a localio filehandle, and calls `nfs_initiate_pgio()`.
- `nfs_initiate_pgio()` sets up an async RPC task on `nfsiod_workqueue`, marks moveable tasks when supported, delegates protocol-specific initiation to `rw_ops`, and can run via `nfs_local_doio()` when localio is available.

## Error and Resend Behavior
- `nfs_set_pgio_error()` records the earliest failed byte and marks the header as errored.
- `nfs_pgio_result()` delegates protocol-specific done/result logic, then records task errors or successful results.
- `nfs_pgio_error()` marks `NFS_IOHDR_REDO` and invokes completion.
- `nfs_pageio_error_cleanup()` calls completion error cleanup on every mirror list when descriptor errors exist.
- `nfs_pageio_resend()` moves a failed header’s requests into a fresh descriptor and resubmits, falling back to cleanup and pgio error recording if resend cannot drain all pages.

## Integration Points
- Exports core helpers used by normal NFS and pNFS paths: `nfs_generic_pgio`, `nfs_pageio_add_request`, `nfs_pageio_complete`, `nfs_pageio_resend`, `nfs_initiate_pgio`, request allocation/free helpers, and page-group synchronization.
- Includes `pnfs.h`, `nfstrace.h`, and `fscache.h`, making it the bridge between generic NFS page-cache writeback/readback and layout-driver-specific routing.

## Invariants and Risks
- Request splitting mutates the original request’s base, offset, and byte count after subrequest submission; callers must not assume the original range is unchanged during batching.
- The page-vector size check prevents slab-unfriendly allocations; changing this logic risks allocation failures or oversized RPC setup.
- Open-context, lock-context, contiguity, and layout/mirror constraints are all part of safe coalescing. Relaxing any one can merge I/O that must remain distinct.
- Concurrency correctness relies heavily on bit locks, `kref`, `io_count`, and descriptor list ownership.
