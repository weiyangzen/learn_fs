# File Research: sources/os/linux/linux-stable/fs/nfs/pagelist.c

This file implements the generic NFS read/write request list machinery. Its main job is to allocate `struct nfs_page` requests, group and split them, coalesce compatible requests into page I/O descriptors, build `struct nfs_pgio_header` RPC payloads, submit asynchronous read/write RPC tasks or local I/O, and recover/resend requests after errors.

Core responsibilities:
- Manage the `nfs_page` slab cache via `nfs_init_nfspagecache()` and `nfs_destroy_nfspagecache()`.
- Allocate, initialize, reference, unlock, release, and free `struct nfs_page` requests.
- Track per-lock-context in-flight I/O with `io_count`, including synchronous waits and RPC task sleeps.
- Maintain page groups through `wb_head` and `wb_this_page`, with `PG_HEADLOCK` locking and group-wide synchronization bits.
- Split large or partially coalescible requests into subrequests while preserving page-group semantics.
- Coalesce page requests into `struct nfs_pageio_descriptor` mirrors and submit page I/O.
- Build RPC arguments and page vectors for read/write calls.
- Support pNFS mirroring through descriptor mirror arrays and mirror-specific request lists.

Important functions:
- `nfs_pgheader_init()` initializes an `nfs_pgio_header` from the current descriptor mirror, including inode, first request, credential, start offset, completion state, direct-request pointer, netfs state, completion ops, and mirror index.
- `nfs_set_pgio_error()` records the earliest failed byte in a page I/O header, clears EOF, marks `NFS_IOHDR_ERROR`, and traces `nfs_pgio_error`.
- `nfs_page_create_from_page()` and `nfs_page_create_from_folio()` allocate requests for page-backed or folio-backed I/O and initialize them as page-group heads.
- `nfs_create_subreq()` creates a locked subrequest, attaches the same page/folio, links it into the existing page group, and copies the retry count.
- `nfs_generic_pg_test()` enforces descriptor block-size limits and page-vector allocation limits before allowing coalescing.
- `nfs_pgio_rpcsetup()` fills NFS read/write RPC arguments: filehandle, offset, page base, page array, byte count, open context, lock context, stability mode, fattr, EOF/result fields, and verifier.
- `nfs_initiate_pgio()` constructs and starts the RPC task, optionally dispatching local I/O through `nfs_local_doio()`.
- `nfs_generic_pgio()` moves requests from a mirror list into the header, constructs the page vector, validates page counts, adjusts conditional stable-write flags, and installs common RPC call ops.
- `nfs_pageio_add_request()` handles pNFS mirror setup, duplicating requests for mirror indices, then adds/coalesces each mirror.
- `nfs_pageio_complete()` drains each mirror, handles recoalescing, invokes error cleanup, runs descriptor cleanup ops, and releases dynamic mirror arrays.
- `nfs_pageio_resend()` moves failed header requests into a new descriptor and retries them through the selected path, cleaning up leftover pages on failure.

Coalescing and splitting behavior:
- Requests can coalesce only when open contexts match, lock owners match if POSIX/flock locks exist, and byte ranges are contiguous.
- If a request is larger than what the current descriptor can accept, `__nfs_pageio_add_request()` creates subrequests and adjusts the original request’s base, offset, and byte count.
- If coalescing fails because the descriptor is full, the file submits current I/O, then may retry the same request or recoalesce pending requests.
- `pg_recoalesce` is used when lower layers request that submitted pages be reprocessed through the descriptor.

Mirroring:
- `nfs_pageio_setup_mirroring()` asks `pg_get_mirror_count()` whether a request needs multiple mirrors.
- Dynamic mirrors are allocated up to `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`.
- Request duplication happens before the original request is submitted to mirror zero.
- Completion loops over all mirrors and restores the original mirror index afterward.

Concurrency and lifetime:
- `PG_BUSY` protects request ownership; `PG_CONTENDED2` wakes waiters in `nfs_unlock_request()`.
- `PG_HEADLOCK` protects page-group traversal and mutation; subrequests hold references on the group head until teardown.
- `PG_TEARDOWN` synchronizes page-group destruction so all group members reach teardown before unlink/free.
- Lock-context `io_count` is incremented on request creation and decremented on request cleanup; wakeups drive unlock-context and asynchronous RPC waits.
- Descriptor error paths centralize cleanup through `pg_completion_ops->error_cleanup()`.

Integration points:
- Includes `pnfs.h` and allows pNFS pageio ops to customize mirrors, tests, initialization, cleanup, and doio.
- Uses `nfstrace.h` for pgio error tracing.
- Exports key symbols used by pNFS and NFS read/write/commit code: current mirror access, header init/free, generic pgio setup, resend, page request management, and generic pageio ops.
