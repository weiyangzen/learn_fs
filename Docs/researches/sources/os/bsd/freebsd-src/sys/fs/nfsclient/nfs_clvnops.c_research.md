# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvnops.c

## Purpose
Implements the FreeBSD new NFS client vnode operation layer for NFSv2, NFSv3, NFSv4, NFSv4.1, and NFSv4.2. It bridges VFS vnode operations to buffer-cache I/O, NFS RPC helpers, NFSv4 state/delegation/locking, pNFS data-server I/O, close-to-open coherency, namecache validation, extended attributes, and newer NFSv4.2 file operations.

## Main Interfaces
- Registers `newnfs_vnodeops` and `newnfs_fifoops`, with signal-deferred bypass wrappers around full nosig operation vectors.
- Implements normal vnode ops for access, lookup, open, close, getattr, setattr, read, readlink, create, mknod, remove, rename, link, symlink, mkdir, rmdir, readdir, strategy, fsync, advisory locks, ACLs, advise, allocate, deallocate, copy file range, ioctl seek-hole/data, extended attributes, and pathconf.
- Exports lower helpers used by bio/node code: `ncl_readlinkrpc()`, `ncl_readrpc()`, `ncl_writerpc()`, `ncl_removeit()`, `ncl_readdirrpc()`, `ncl_readdirplusrpc()`, `ncl_commit()`, and `ncl_flush()`.

## Key Behavior
- Access checks use NFSv3/v4 `ACCESS` RPCs with per-UID `n_accesscache` entries and KDTRACE probes. NFSv2 falls back to local mode checks plus a root-read probe to catch root-squash style denial.
- `nfs_open()` performs NFSv4 `OPEN` before cache validation, enforces close-to-open coherency by comparing cached mtime/change attributes, invalidates buffers when local or remote changes are detected, tracks direct I/O opens with `NNONCACHE`, records write credentials for later pageout, and flushes executable text mappings before execution.
- `nfs_close()` cleans dirty pages, flushes/commits modified buffers according to protocol and mount policy, updates NFSv4 change attributes, sends NFSv4 `CLOSE`, returns delayed write errors, and unwinds direct I/O state.
- `nfs_getattr()` prefers the attribute cache, can prime the access cache, overlays local delegation modify time, and maps NFSv4 protocol errors. `nfs_setattr()` validates supported flags, handles truncation through `ncl_meta_setsize()` and `ncl_vinvalbuf()`, rolls back size on RPC failure, and updates delegation/local modification time.
- `nfs_lookup()` integrates namecache hits, negative cache validation, parent directory mtime/ctime checks, named attribute directories, NFSv4 remove-in-progress waits, dot/dotdot locking rules, RPC lookup, vnode instantiation, stale-attribute suppression using `n_localmodtime`, and cache insertion with timestamps.
- Create-like operations issue protocol-specific RPCs, load parent/child post-op attributes when available, use lookup fallback when no file handle is returned, update namecache entries when safe, and mark parent directories modified.
- Remove and rename implement sillyrename for active unlinked files, cache purging, NFSv4 no-CTO delegation cleanup based on remove status, directory remove-in-progress serialization, and ENOENT-to-success retry handling for idempotent retransmit cases.
- Directory reading validates `DIRBLKSIZ` alignment, uses logical offset to NFS cookie maps, maintains EOF offset cache, supports `READDIRPLUS`, and purges namecache entries at offset zero when readdirplus will repopulate them.
- `ncl_flush()` is the central dirty-buffer write/commit engine. It gathers `B_DELWRI | B_NEEDCOMMIT` buffers, commits ranges with shared or per-buffer credentials, handles stale write verifiers, writes remaining dirty buffers, waits for output under signal/renew-thread constraints, performs pNFS layoutcommit, clears `NMODIFIED` when fully clean, and retries boundedly if buffers remain.
- Advisory locking routes non-v4 locks through lockd or local lockf depending on mount flags; NFSv4 locks call `nfsrpc_advlock()`, flush before unlocking write-locked ranges, wait/retry for blocking locks, and invalidate caches after acquiring locks for RFC3530 coherency.
- NFSv4 ACL operations call `nfsrpc_getacl()` and `nfsrpc_setacl()`, mapping unsupported/remote errors into VFS-visible results.
- NFSv4.2 support includes `VOP_ADVISE`, `VOP_ALLOCATE`, `VOP_DEALLOCATE`, server-side copy/clone with fallback to generic copy, `FIOSEEKDATA`/`FIOSEEKHOLE`, and RFC8276 user extended attributes.
- `nfs_pathconf()` probes server capabilities for pathconf values, ACL models, named attributes, clone block size, case-insensitivity, and seek-hole support; it fakes stable defaults for older protocols and unsupported names.

## Important State
- Sysctls tune access-cache timeout, access-cache priming, commit-on-close, clean-pages-on-close, direct I/O behavior, dirty-page retry, direct-I/O mmap allowance, and maximum allocate/deallocate RPC length.
- Uses `struct nfsnode` flags including `NMODIFIED`, `NWRITEERR`, `NNONCACHE`, `NDELEGMOD`, `NREMOVEINPROG`, `NREMOVEWANT`, `NNOLAYOUT`, `NWRITEOPENED`, `NHASBEENLOCKED`, `NDSCOMMIT`, `NMIGHTBELOCKED`, and `NNAMEDNOTSUPP`.
- Uses `struct nfsmount` flags/private flags for protocol version, no-CTO, pNFS, one-open-owner, no-copy, no-consecutive-copy, seek support/tested, no-xattr, no-advise, no-allocate, no-deallocate, and clone block size.
- Tracks local modification time (`n_localmodtime`) to reject stale RPC attributes that race with local size-changing operations.

## Dependencies
Depends on VFS vnode/namecache/locking APIs, buffer cache and VM pager APIs, `lockf`/lockd integration, NFS client RPC entry points from `nfs_clrpcops.c`, node and mount definitions in `nfsnode.h`/`nfsmount.h`, pNFS layout/data-server helpers, NFSv4 delegation/state helpers, KDTRACE macros, FreeBSD extattr/ioctl/pathconf APIs, and kernel credential handling.

## Risks and Edge Cases
- Cache coherency spans attribute stamps, mtime/change attributes, namecache timestamps, directory cookies, delegation state, dirty buffers, and close/open flushes; small changes can regress stale-data or excessive-RPC behavior.
- `ncl_flush()` has high deadlock and data-loss sensitivity because it interleaves buffer locking, commit RPCs, signal handling, async output waits, verifier recovery, pNFS layoutcommit, and vnode dirty-state clearing.
- NFSv4 named attribute handling changes lookup/create directory targets and disables namecache insertion; incorrect flag handling can return normal files for named-attribute paths or vice versa.
- Copy/clone has many fallbacks: intra-file clone constraints, cross-mount rejection, output credential retry, consecutive-copy fallback, stale verifier restart, and permanent mount disablement for unsupported server behavior.
- Extended attribute errors are protocol-specific and update a mount-wide `NOXATTR` flag on unsupported/illegal operation replies.
- Sillyrename intentionally approximates local unlink semantics over NFS but has race windows and depends on later inactive cleanup.
