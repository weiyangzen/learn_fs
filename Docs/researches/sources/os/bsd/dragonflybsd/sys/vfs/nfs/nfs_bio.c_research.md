# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_bio.c

## Role

Implements NFS client buffered I/O through DragonFly’s buffer/BIO layer. It handles read caching, directory and symlink reads, write buffering, file-size extension/truncation metadata, async BIO dispatch, synchronous BIO execution, and NFSv3 unstable write/commit handling.

## Major Entry Points

- `nfs_bioread()` services vnode reads for regular files, symlinks, and directories.
- `nfs_write()` services regular-file writes through buffer-cache blocks.
- `nfs_vinvalbuf()` flushes and invalidates vnode buffers with NFS interruptible-mount semantics.
- `nfs_asyncok()` decides whether async NFS BIO submission is currently allowed.
- `nfs_asyncio()` queues a BIO for the per-mount IOD writer thread.
- `nfs_startio()` starts an asynchronous BIO after the writer thread dequeues it.
- `nfs_doio()` executes a BIO synchronously and returns its error.
- `nfs_meta_setsize()` updates `n_size` and calls VM buffer truncate/extend helpers.
- `nfs_readrpc_bio()` and `nfs_readrpc_bio_done()` implement asynchronous BIO read RPCs.
- `nfs_writerpc_bio()` and `nfs_writerpc_bio_done()` implement asynchronous BIO write RPCs.
- `nfs_commitrpc_bio()` and `nfs_commitrpc_bio_done()` implement asynchronous NFSv3 commit RPCs.

## Implementation Notes

- `nfs_bioread()` checks NFSv3 FSINFO lazily before enforcing max file size.
- Approximate cache consistency is maintained by invalidating modified directories, refreshing attributes, and flushing buffers when remote modifications are detected.
- Regular-file reads issue readahead only when async BIO queues and IOD threads are healthy.
- Directory reads use `NFS_DIRBLKSIZ` buffers, cache directory EOF in `n_direofoffset`, and recover from `NFSERR_BAD_COOKIE` by invalidating and rereading directory blocks from the beginning.
- `nfs_check_dirent()` validates server-supplied directory records so arbitrary seek offsets cannot panic the kernel.
- Writes take the mount token, honor pending `NWRITEERR`, load FSINFO, flush local modifications for append or sync writes, and use `nfs_rslock()` for append/extension races.
- File extension updates `n_size` before acquiring buffers so VM/buffer state matches the new logical size.
- Discontiguous dirty ranges in a single buffer force the old dirty range out before accepting the new write, avoiding client-side merging that would worsen multi-client coherency.
- Non-sync full-buffer writes may use async unstable NFSv3 writes when `nfs_async` is enabled; otherwise they stay as delayed writes.
- `nfs_getcacheblk()` uses `GETBLK_PCATCH` for interruptible mounts and stores the logical byte offset directly in `bio_offset`.
- `nfs_asyncio()` tags the BIO with its vnode, inserts it into `nm_bioq`, increments `nm_bioqlen`, and wakes the IOD writer.
- `nfs_startio()` uses dedicated BIO RPC paths for regular-file async reads/writes/commits; symlink and directory async paths are disabled and fall back to synchronous `nfs_doio()`.
- `nfs_doio()` converts BIOs to kernel `uio` operations, handles short-read zero fill, text-file modification kill behavior, directory readdirplus fallback, and synchronous write/commit logic.
- NFSv3 write verifier changes call `nfs_clearcommit()` and force pending unstable data to be rewritten or recommitted.
- Commit failure chains back to a write RPC so dirty data is not silently discarded.

## Dependencies

Uses NFS RPC marshalling helpers, `nfsm_info` request state, NFS mount/node structures, NFS IOD wakeups, buffer cache, BIO callbacks, VM vnode buffer resize APIs, vnode pager sizing, tokens, and NFSv2/v3 protocol constants.

## Research Notes

This file is the client data-path bridge between DragonFly’s VM/buffer cache and NFS RPCs. The highest-risk logic centers on dirty-range accounting, NFSv3 unstable write verifier handling, directory cookie recovery, and async queue state shared with `nfs_iod.c`.
