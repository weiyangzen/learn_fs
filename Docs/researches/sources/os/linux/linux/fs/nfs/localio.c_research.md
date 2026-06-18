# File Research: sources/os/linux/linux/fs/nfs/localio.c

## Purpose
Implements NFS client LOCALIO support. When the NFS server is local to the same kernel, reads, writes, and commits can bypass network RPC and operate directly on an `nfsd_file`, while preserving normal NFS pgio and commit completion semantics.

## Main Concepts
- LOCALIO detection uses the auxiliary `nfslocalio` RPC program and `UUID_IS_LOCAL`.
- A client is local only when UUID state maps to local server state and `localio_enabled` is true.
- Data I/O still completes through NFS RPC-style callbacks so upper NFS layers see normal `nfs_pgio_header` and `nfs_commit_data` completion.

## Key Data Structures
- `struct nfs_local_kiocb` wraps a `kiocb`, bvec array, target pgio header, work item, local `nfsd_file`, and up to three iterators for direct-I/O splitting.
- `struct nfs_local_fsync_ctx` tracks local commit/fsync work and optional synchronous completion.
- `struct nfs_local_dio` is declared in `internal.h` and describes misaligned start, aligned middle, and misaligned end extents.

## Probe and Open Path
- XDR helpers encode/decode the UUID probe.
- `nfs_init_localioclient()` binds the auxiliary localio program to an existing NFS RPC client.
- `nfs_server_uuid_is_local()` sends `UUID_IS_LOCAL` and verifies local UUID state.
- `nfs_local_probe()` disables LOCALIO if globally disabled or auth is not `AUTH_SYS`; otherwise it probes and enables local state.
- `nfs_local_probe_async()` queues probing on `nfsiod_workqueue`.
- `nfs_local_open_fh()` opens read-only or read-write cached local file handles via `nfs_open_local_fh()` and reprobes on selected failures.

## Read/Write Path
- `nfs_local_iocb_alloc()` allocates local I/O state, bvecs, and sets GFP_NOFS context on the backing mapping.
- `nfs_local_iters_init()` converts the NFS page array into bvec-backed iterators.
- Direct I/O support queries nfsd alignment, splits requests into up to three iterators, and uses `IOCB_DIRECT` only for aligned extents.
- `nfs_local_call_read()` and `nfs_local_call_write()` invoke `read_iter()` / `write_iter()` under file credentials on `nfslocaliod_workqueue`.
- Writes set sync flags from NFS stable-write mode and use a local boot verifier.
- Short writes mark the open context for synchronous writes.

## Completion and Commit
- `nfs_local_pgio_done()` accumulates counts and maps negative errno values to NFS status values.
- AIO completions are bounced to `nfsiod_workqueue` because they may occur in bottom-half context.
- `nfs_local_read_done()` clears `res.replen` to avoid corruption if falling back to normal RPC and sets EOF from local file size.
- `nfs_local_vfs_getattr()` refreshes fattr fields after local writes, including NFSv4 change attribute behavior.
- `nfs_local_commit()` runs `vfs_fsync_range()` asynchronously or synchronously, fills commit verifier/status, and releases through normal commit callbacks.

## Research Notes
The sensitive areas are DIO alignment splitting, preserving callback ordering, resetting the boot verifier on errors, avoiding reclaim recursion with GFP flags, and keeping LOCALIO fallback compatible with normal RPC completion paths.
