# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.h

## Scope

This header defines SMBFS node structures, directory cache placeholders, custom rwlock state, node-cache AVL identity fields, smbnode state fields, and node flag bits.

## APIs And Definitions

- `rddir_cache` describes a whole-directory cache entry, though comments state directory caching is not yet active.
- `smbfs_rwlock_t` is a homegrown reader/writer lock that supports interruptible entry and writer re-entry.
- `smbfs_node_hdr_t` contains AVL linkage and remote path identity fields used by the per-mount node cache.
- `smbnode_t` is the SMBFS inode-equivalent, containing mount/vnode pointers, free-list links, rw locks, state lock, open file and directory search handle state, credentials, readahead state, map counts, flags, readdir cache AVL, modified address tracking, delete-map tracking, cached SMB attributes, ACL cache, pseudo-inode, uid/gid, and mode.
- Defines `n_flag` bits such as flush in progress, modified, parent reference, IDs known, readdir serialization, mapped, attribute changed, allocating, waiting allocation, and XATTR.
- Defines `r_flags` bits for dirty data, stale handles, modification/commit state, hashed state, direct I/O, lookup, write-attribute origin, and delmap tracking.
- Provides `VTOSMB()`, `SMBTOV()`, and `SMBFS_DNP_SEP()` helpers.

## Locking Contract

- Header comments document lock roles and ordering: `r_rwlock > r_lkserlock > r_statelock`.
- `r_rwlock` serializes writes/setattr and directory reads/updates.
- `r_lkserlock` serializes lock requests with map/write/readahead operations.
- `r_statelock` protects most smbnode fields, including 64-bit `r_size`.

## Risks And Invariants

- `r_size` must be read/written under `r_statelock` on 32-bit architectures.
- `n_rpath` and `n_rplen` define node identity in the AVL cache.
- XATTR directory separator behavior changes path construction via `SMBFS_DNP_SEP()`.
