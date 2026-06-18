# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clsubs.c

## Purpose

Provides small support routines for the NFS client module: initialization, module uninitialization policy, directory cookie locking and lookup, vnode lock upgrade/downgrade helpers, attribute-cache validation, and write-verifier commit reset.

## Key Entry Points

- `ncl_init()` initializes async I/O daemon state, the new nfsiod task, and the nfsnode hash table.
- `ncl_uninit()` currently returns `EOPNOTSUPP`; NFS client module unload is explicitly unsupported.
- `ncl_dircookie_lock()` and `ncl_dircookie_unlock()` serialize access to per-directory cookie maps with `NDIRCOOKIELK`.
- `ncl_upgrade_vnlock()` upgrades a shared vnode lock to exclusive and returns the old lock mode.
- `ncl_downgrade_vnlock()` restores the original shared lock when needed.
- `ncl_getattrcache()` validates and returns cached vnode attributes.
- `ncl_getcookie()` maps logical directory offsets to NFS directory cookies.
- `ncl_invaldir()` invalidates directory cookie/verifier state.
- `ncl_clearcommit()` clears `B_NEEDCOMMIT` and `B_CLUSTEROK` on delayed-write buffers after a write verifier change.

## Attribute Cache Logic

`ncl_getattrcache()` computes a timeout based on cached mtime age, mount attribute-cache limits, vnode type, and whether local modifications require flushing. It returns `ENOENT` on cache miss and updates `nfsstatsv1.attrcache_misses`.

On cache hit it:

- updates `np->n_size` and pager size when cached size differs
- preserves locally changed atime/mtime when `NCHG`, `NACC`, or `NUPD` are set
- copies cached attributes into the caller’s `vattr`
- records DTrace attr-cache hit/miss probes

The call to `nfscl_mustflush(vp)` is deliberately made before locking the node mutex.

## Directory Cookie Handling

`ncl_getcookie()` stores NFS readdir cookies in linked `struct nfsdmap` blocks. It treats offset zero or negative offsets as the null cookie. For positive offsets it converts the logical offset to a cookie index based on `NFS_DIRBLKSIZ`, walks/extends the cookie block list, and optionally allocates new blocks when `add` is true.

`ncl_invaldir()` resets EOF offset, cookie verifier, and the first cookie map’s effective cookie count. It does not free all cookie blocks; it invalidates the logical contents.

## Commit Verifier Handling

`ncl_clearcommit()` walks all vnodes on a mount and scans dirty buffer queues. For unlocked dirty buffers marked both `B_DELWRI` and `B_NEEDCOMMIT`, it clears `B_NEEDCOMMIT` and `B_CLUSTEROK`.

This supports server reboot/write verifier changes: unstable writes must be rewritten before later COMMITs can be trusted.

## Integration Points

- Uses `nfscl_mustflush()` from NFSv4 state/delegation logic.
- Uses `ncl_nhinit()` to initialize nfsnode state.
- Uses async daemon globals `ncl_iodwant`, `ncl_iodmount`, `ncl_numasync`, and `ncl_iodmax`.
- Uses vnode/buffer iteration macros and buffer object locks.
- Updates global NFS statistics and DTrace probes.

## Concurrency Notes

- Directory cookie lock is a flag protected by `np->n_mtx` and `msleep`/`wakeup`.
- Attribute cache reads and size adjustments are protected by `np->n_mtx`.
- Commit clearing uses mount vnode iteration plus per-vnode buffer-object locks.
- Vnode lock upgrade/downgrade helpers assert expected starting lock state.

## Risks And Edge Cases

- `ncl_uninit()` leaves unload unsupported, so cleanup paths under `#if 0` are not active.
- Directory cookie invalidation only resets the first map’s end marker; stale allocated maps remain but are logically unreachable until rebuilt.
- Attribute cache timeout behavior depends on local modification flags and delegation flush policy.
- `ncl_clearcommit()` skips locked buffers, so later passes must handle them.

## Verification Ideas

- Attribute-cache tests for modified regular files, directories, zero `n_attrstamp`, and delegation no-flush behavior.
- Directory cookie tests for offset zero, negative offset, sparse lookup without add, and multi-map allocation.
- Write verifier reset tests with locked/unlocked dirty buffers and `B_CLUSTEROK` clearing.
