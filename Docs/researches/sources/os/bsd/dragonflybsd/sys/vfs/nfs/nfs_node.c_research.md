# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_node.c

This file manages DragonFlyBSD NFS client vnode-to-`nfsnode` identity. It provides the hash table used to map NFS file handles to active vnodes and performs reclaim/inactive cleanup.

Primary responsibilities:
- Initialize and destroy the global `nfsnode` hash table.
- Find or create an `nfsnode` for a file handle.
- Provide blocking and nonblocking lookup variants.
- Handle vnode inactive and reclaim paths.

Key functions:
- `nfs_nhinit()` sizes and allocates the hash using `vfs_inodehashsize()`, and initializes `nfsnhash_lock`.
- `nfs_nhdestroy()` releases the hash table.
- `nfs_nget()` looks up an existing node by mount plus file handle, safely `vget()`s the vnode, detects `notvp` collisions, or allocates a new vnode/node pair.
- `nfs_nget_nonblock()` mirrors `nfs_nget()` but returns `EWOULDBLOCK` when an existing vnode cannot be locked immediately.
- `nfs_inactive()` handles sillyrename cleanup for removed-but-open files, invalidates buffers, calls `nfs_removeit()`, clears transient node flags, and recycles removed vnodes.
- `nfs_reclaim()` removes the node from the hash, breaks vnode/node back-pointers, frees directory cookies, large file handles, read/write credentials, and the object-cache allocation.

Concurrency and race handling:
- `nfsnhash_token` protects hash traversal and vnode/node cross-links.
- `nfsnhash_lock` serializes allocation paths that may block.
- After blocking allocation, code revalidates that no competing `nfs_nget()` inserted the same file handle.
- Reclaim clears `np->n_vnode` before freeing so concurrent hash lookups can detect stale references.

Important interactions:
- Uses `fnv_32_buf()` over file-handle bytes to select buckets.
- Depends on per-mount object cache `nmp->nm_mnode`.
- Uses vnode lifecycle helpers `getnewvnode()`, `vx_downgrade()`, `vx_put()`, `vput()`, `vrecycle()`.
- Directory cookie memory freed here is allocated and managed by helpers in `nfs_subs.c`.

Caveats:
- The blocking and nonblocking paths intentionally duplicate logic; changes must keep their race checks aligned.
- Collision handling with `notvp` returns `ESTALE` to avoid client-client rename/link/symlink confusion.
