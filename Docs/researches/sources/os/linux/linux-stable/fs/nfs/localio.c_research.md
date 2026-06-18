# File Research: sources/os/linux/linux-stable/fs/nfs/localio.c

## Purpose
Implements NFS client LOCALIO support: when the NFS server is local to the same kernel, the client can bypass the network RPC data path and perform reads, writes, and commits directly against an `nfsd_file`.

## Main Concepts
- LOCALIO detection uses a small auxiliary RPC program, `nfslocalio`, with `UUID_IS_LOCAL`.
- A client is considered local when its UUID maps to local server state and `localio_enabled` is true.
- Data I/O is still shaped like NFS pgio/commit completion: local operations fill NFS result structures and invoke the same RPC completion callbacks expected by the upper NFS client layers.

## Key Data Structures
- `struct nfs_local_kiocb`
  - Wraps a `kiocb`, bio_vec array, target `nfs_pgio_header`, work item, completion callback work hook, local `nfsd_file`, and up to three `iov_iter`s for DIO splitting.
- `struct nfs_local_fsync_ctx`
  - Tracks local commit/fsync work, the target `nfsd_file`, `nfs_commit_data`, work item, and optional synchronous completion.
- `struct nfs_local_dio` is declared in `internal.h` and filled here to describe misaligned start, aligned middle, and misaligned end extents.

## LOCALIO Probe Path
- `localio_xdr_enc_uuidargs()` / `localio_xdr_dec_uuidres()` encode/decode the UUID probe.
- `nfslocalio_program` declares the auxiliary RPC program.
- `nfs_init_localioclient()` binds the auxiliary RPC program to an existing NFS RPC client.
- `nfs_server_uuid_is_local()` sends `UUID_IS_LOCAL`, then checks that required local UUID fields were initialized.
- `nfs_local_probe()` enables or disables localio based on module parameter, AUTH_SYS requirement, UUID state, and probe result.
- `nfs_local_probe_async_work()` and `nfs_local_probe_async()` queue probing on `nfsiod_workqueue`.

## Opening Local File Handles
- `nfs_local_open_fh()` checks local status and allowed mode, selects cached read-only or read-write local file slot, and calls `__nfs_local_open_fh()`.
- `__nfs_local_open_fh()` uses `nfs_open_local_fh()` and retriggers probing on selected failures such as `-ENOMEM`, `-ENXIO`, and `-ENOENT`.
- Local file references are released through `nfs_local_file_put()`.

## Read/Write Data Path
- `nfs_local_iocb_alloc()` builds a local `kiocb`, allocates bvecs, sets `GFP_NOFS` on the backing mapping, and initializes position/flags.
- `nfs_local_iters_init()` converts the NFS page array and pgbase/count into bvec-backed iterators.
- Direct I/O support:
  - `nfs_is_local_dio_possible()` queries server-side DIO alignment and splits the request.
  - `nfs_local_iters_setup_dio()` creates up to three iterators: misaligned start, aligned middle, misaligned end.
  - The aligned middle can run with `IOCB_DIRECT`; misaligned portions fall back to buffered I/O.
- `nfs_local_do_read()` queues `nfs_local_call_read()` on `nfslocaliod_workqueue`.
- `nfs_local_call_read()` runs `read_iter()` under the file credentials and handles immediate, queued, short, and error completions.
- `nfs_local_do_write()` sets sync flags according to NFS stable-write mode, sets a local write verifier, and queues `nfs_local_call_write()`.
- `nfs_local_call_write()` runs `write_iter()` with `PF_LOCAL_THROTTLE | PF_MEMALLOC_NOIO`, handles short writes by marking the open context for synchronous writes, and ends file write accounting.
- AIO completion callbacks queue final callback processing to `nfsiod_workqueue` because completion can occur in bottom-half context.

## Completion and Result Handling
- `nfs_local_pgio_done()` accumulates byte counts, maps negative errors to NFSv4-style status values, and tracks multi-iterator completion.
- `nfs_local_read_done()` clears `res.replen` to avoid corrupt behavior if falling back to normal RPC, and sets EOF based on file size.
- `nfs_local_write_done()` resets boot verifier on errors.
- `nfs_local_vfs_getattr()` refreshes selected fattr fields from VFS after writes, including v4 change attribute handling.
- `nfs_local_pgio_release()` invokes normal RPC call-done/release callbacks and supports restart if the callback installs a new task action.

## Commit Path
- `nfs_local_commit()` allocates an fsync context, initializes task ops, and queues `nfs_local_fsync_work()`.
- `nfs_local_run_commit()` calls `vfs_fsync_range()` for the requested range.
- `nfs_local_commit_done()` sets verifier/op status on success or maps errors on failure.
- Synchronous commits use stack completion and wait for work completion.

## Configuration and Controls
- `localio_enabled` module parameter globally enables/disables localio.
- LOCALIO requires AUTH_SYS in `nfs_local_probe()`.
- Direct I/O alignment is delegated to nfsd through `nfs_to->nfsd_file_dio_alignment()`.

## Research Notes
This file is a bridge between client-side NFS page I/O semantics and local VFS file operations. The subtle parts are completion ordering, DIO splitting, verifier generation/reset, memory reclaim flags, and preserving normal RPC callback semantics even when no network RPC was used.
