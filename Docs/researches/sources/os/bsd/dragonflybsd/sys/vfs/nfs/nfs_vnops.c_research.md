# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vnops.c

## Purpose

`nfs_vnops.c` implements the vnode operation layer for NFSv2/NFSv3 client files, directories, symlinks, special devices, and FIFOs. It translates VFS operations into NFS RPCs and coordinates local cache, buffer, namecache, credential, and weak-cache-consistency state.

## Vnode Operation Tables

- `nfsv2_vnode_vops` supplies normal file/directory operations: access, open/close, getattr/setattr, read/write, lookup/nresolve, create/mknod/remove/rename/link/symlink/mkdir/rmdir, readdir, strategy, fsync, reclaim/inactive, kqueue filter.
- `nfsv2_spec_vops` wraps special-device access, close, fsync, getattr, inactive, print, reclaim, setattr, with no direct read/write.
- `nfsv2_fifo_vops` delegates FIFO behavior to fifofs while preserving NFS metadata updates.

## Main Client Operations

- Access/open/close:
  - `nfs_access()` maps VFS access bits to NFSv3 `ACCESS`, caches access results by UID, falls back to local attribute checks for v2, and saves validated read/write credentials.
  - `nfs_open()` validates types, updates stored credentials, reconciles local vs remote modifications, and invalidates buffers when needed.
  - `nfs_close()` flushes dirty regular-file buffers; v3 may write-only or write+commit depending on `nfsv3_commit_on_close`.
- Attributes:
  - `nfs_getattr()` serves cached attributes, optionally refreshes via v3 `ACCESS`, then performs `GETATTR`.
  - `nfs_setattr()` handles truncation, readonly checks, time changes, write flushes, local size rollback on error, and calls `nfs_setattrrpc()`.
  - `nfs_setattrrpc()` encodes v2/v3 setattr requests and decodes v3 WCC data or v2 attributes.
- Lookup/namecache:
  - `nfs_nresolve()` is the newer namecache resolver using `LOOKUP`, negative/positive timeout caching, file-handle conversion, and v3 postop attrs.
  - `nfs_lookup()` is the old lookup API, still present for incomplete new-API coverage, handling parent locking, dotdot, rename/delete/create semantics, and NFS file-handle matching.
  - `nfs_lookitup()` is an internal helper for retry lookup, sillyrename, and v2/v3 fallback cases.
- Data I/O:
  - `nfs_read()` and `nfs_readlink()` use `nfs_bioread()`.
  - `nfs_readlinkrpc_uio()`, `nfs_readrpc_uio()`, and `nfs_writerpc_uio()` issue synchronous READLINK/READ/WRITE RPCs and handle v2/v3 differences, short reads, EOF, zero-fill, write verifiers, and commit requirements.
  - `nfs_strategy()` pushes a bio and routes sync I/O directly to `nfs_doio()` or async I/O to `nfs_asyncio()`.
  - `nfs_bmap()` is an identity mapping because NFS uses byte offsets, not local disk block mapping.
- Directory operations:
  - `nfs_readdir()` validates directory state, consults EOF cache, and uses buffered reads.
  - `nfs_readdirrpc_uio()` converts NFS READDIR replies into `struct nfs_dirent` records and maintains logical-offset-to-cookie mappings.
  - `nfs_readdirplusrpc_uio()` additionally populates namecache/vnode entries from returned attributes and file handles when safe.
- Mutating namespace operations:
  - `nfs_create()`, `nfs_mknodrpc()`, `nfs_mknod()`, `nfs_symlink()`, and `nfs_mkdir()` encode create-style RPCs and fall back to lookup when replies lack usable file handles.
  - `nfs_remove()` implements stateless-NFS-compatible sillyrename for active unlinked files.
  - `nfs_removeit()` and `nfs_removerpc()` remove delayed sillyrename names.
  - `nfs_rename()` handles cross-device checks, optional flush-before-rename, target sillyrename, notifications, and retry `ENOENT` mapping.
  - `nfs_link()` issues hard-link RPCs and optionally flushes source data before linking.
  - `nfs_rmdir()` issues directory removal and maps retry `ENOENT` to success.
- Flush/commit:
  - `nfs_fsync()` calls `nfs_flush(..., commit=1)`.
  - `nfs_flush()` scans dirty buffer trees, writes new dirty buffers, optionally performs NFSv3 COMMIT on `B_NEEDCOMMIT` buffers, waits for pending writes, handles interruptible mounts, and reports deferred write errors.
  - `nfs_flush_bp()` and `nfs_flush_docommit()` collect commit ranges and complete or re-dirty buffers based on commit outcome.
  - `nfs_commitrpc_uio()` issues NFSv3 COMMIT and validates write verifiers.
- Miscellaneous:
  - `nfs_advlock()` uses local `lf_advlock()` as a placeholder for absent lockd integration.
  - FIFO wrappers track access/update times and call fifofs operations.
  - Kqueue filter support wires read/write/vnode knotes to vnode pollinfo.

## Notable Details

- The file uses `nm_token` widely to serialize mount-local NFS client state.
- Multiple sysctls tune correctness/performance tradeoffs: rename flushing, hard-link flushing, access cache timeout, positive/negative namecache timeout, and close-time v3 commit.
- Several retry kludges intentionally map idempotency/race responses to success, such as `ENOENT` after retransmitted remove/rename and `EEXIST` after create/link/mkdir/symlink retries.
- Directory cookies are maintained in block-sized logical offset maps, and missing cookies are treated as `NFSERR_BAD_COOKIE`.
- NFSv2 READDIR is called out as unsafe for HAMMER-style directory cookies.
- Readdirplus avoids caching degenerate `.`/`..` names and identical directory file handles.
- `nfs_flush()` uses negative error values internally because RB scan callbacks use negative returns to stop scans.

## Integration

This file is the main consumer of `nfsm_subs.c` request-building/parsing helpers, `nfsnode.h` per-vnode state, `nfsmount.h` mount state, `nfs_bio.c` buffer I/O, and `nfs_node.c` nfsnode allocation/cache functions.
