# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvnops.c

## Purpose
Implements the main vnode operation layer for the “newnfs” client, covering NFSv2, NFSv3, and NFSv4 regular vnode operations plus FIFO wrappers and buffer write operations. It is the bridge between NetBSD/FreeBSD-style VFS vnode calls and lower NFS RPC helpers such as `nfsrpc_*`, `ncl_bioread`, `ncl_doio`, `ncl_flush`, and NFSv4 delegation/state helpers.

## Main Interfaces
- Exports `newnfs_vnodeops`, the vnode op vector for normal NFS vnodes: lookup, open, close, getattr, setattr, read/write, create/remove/rename/link, directory ops, strategy, fsync, ACL, locks, and paging hooks.
- Exports `newnfs_fifoops`, the vnode op vector for NFS-hosted FIFOs, wrapping FIFO operations while updating NFS-side access/update timestamps.
- Exports lower helper entry points used by other NFS client modules: `ncl_readlinkrpc`, `ncl_readrpc`, `ncl_writerpc`, `ncl_readdirrpc`, `ncl_readdirplusrpc`, `ncl_commit`, `ncl_flush`, `ncl_removeit`, and `ncl_writebp`.
- Exports `buf_ops_newnfs`, connecting buffer-cache writes to `nfs_bwrite`/`ncl_writebp`.

## Key Behavior
- `nfs_access` implements local read-only mount checks, NFSv3/v4 `ACCESS` RPC checks, access-result caching by UID, and NFSv2 fallback behavior using local mode checks plus a root-read probe.
- `nfs_open` performs NFSv4 `OPEN` before cache validation, then enforces close-to-open coherency by comparing cached modify/change state, invalidating buffers when needed, handling `O_DIRECT`, and storing write credentials for later pageout.
- `nfs_close` pushes dirty VM pages and buffers on close, handles NFSv3 commit policy, NFSv4 close/delegation requirements, propagates delayed write errors, updates change attributes, and unwinds direct I/O open state.
- `nfs_getattr` first consults the attribute cache, optionally primes the access cache, falls back to `GETATTR`, and overlays delegated local modify time.
- `nfs_setattr` validates unsupported fields, handles truncation carefully through `ncl_meta_setsize` and buffer invalidation, rolls back size on RPC failure, and invalidates access/delegation state through `nfs_setattrrpc`.
- `nfs_lookup` combines namecache hits with NFS attribute/change validation, negative cache validation, NFSv4 remove-in-progress waits, special dot/dotdot locking rules, RPC lookup, node instantiation, and namecache entry creation.
- Create-like operations (`nfs_create`, `nfs_mknod`, `nfs_symlink`, `nfs_mkdir`) issue RPCs, load returned attributes when present, perform lookup fallback when handles are not returned, and mark parent directories modified.
- Remove/rename behavior includes sillyrename support for active files, directory and vnode cache purging, ENOENT retry-success mapping for idempotency edge cases, NFSv4 name metadata updates, and parent attr invalidation.
- Directory reads use logical offset to NFS cookie mapping through `ncl_getcookie`, EOF offset caching, and separate `READDIR`/`READDIRPLUS` RPC paths.
- `ncl_flush` is the central dirty-buffer flush/commit loop: it collects `B_NEEDCOMMIT` buffers, issues range commits, handles stale write verifiers, writes dirty buffers, waits for output/direct I/O completion, updates `NMODIFIED`, and retries boundedly.
- Advisory locking supports NFSv4 byte-range locks via RPC with RFC3530 coherency flush/invalidation behavior, and falls back to local/lockd paths for older NFS depending on mount flags.
- NFSv4 ACL vnode ops delegate to `nfsrpc_getacl`/`nfsrpc_setacl`; `nfs_pathconf` uses NFS pathconf/getattr where useful and fakes stable POSIX values otherwise.

## Important State
- Uses `struct nfsnode` fields including `n_flag`, `n_size`, `n_vattr`, `n_attrstamp`, `n_accesscache`, `n_mtime`, `n_change`, `n_direofoffset`, `n_cookies`, `n_sillyrename`, `n_directio_opens`, `n_directio_asyncwr`, and `n_writecred`.
- Uses `struct nfsmount` fields for mount flags, negative/positive namecache timeouts, pNFS capability, async I/O, write verifier state, and timeout/interruption behavior.
- Sysctls tune access cache timeout, access-cache priming, commit-on-close, clean-pages-on-close, direct I/O behavior, and dirty-page retry policy.

## Dependencies
Depends heavily on `nfsnode.h`, `nfsmount.h`, client RPC helpers, NFSv4 state/delegation helpers, VFS namecache and vnode locking APIs, VM object/page cleaning APIs, buffer-cache APIs, lockf/lockd integration, and DTrace probe macros from `nfs_kdtrace.h`.

## Risks and Edge Cases
- Cache coherency is distributed across namecache timestamps, attribute cache stamps, delegation state, directory EOF cookies, and close/open flushes; changes must preserve these interactions.
- `ncl_flush` has complex buffer locking, two-pass commit/write behavior, and signal/forced-unmount exits; regression risk is high for deadlocks, dirty-buffer loss, and spurious EINTR/EIO.
- Sillyrename intentionally approximates local unlink semantics over stateless NFS and has race windows with other clients.
- NFSv4 error mapping and state-sequence handling are delegated to lower RPC/state layers; vnode ops often must map only after RPC helpers return protocol errors.
- The file carries FreeBSD-derived API assumptions and NetBSD porting glue, so portability edits need careful kernel API verification.
