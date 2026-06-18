# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_shadow.c

Purpose: Implements NFSv4 client shadow vnodes for regular-file hard-link/name disambiguation.

Key behavior:
- `vtosv` maps a vnode back to its owning `svnode_t`, checking the master vnode first and then the rnode shadow list.
- `sv_activate` initializes the master shadow vnode for new rnodes or replaces an existing master vnode reference with a matching shadow vnode when needed.
- `sv_find` finds a shadow vnode matching parent directory filehandle and component name, or allocates a new shadow vnode sharing the master rnode.
- `sv_match` compares by `nfs4_fname_t` identity and parent shared filehandle.
- `sv_inactive` removes and destroys inactive shadow vnodes and releases the master vnode reference they hold.
- `sv_exchange` replaces a shadow vnode reference with the master vnode, used when operations need resources owned only by the master vnode.
- Initializes/finalizes the `svnode_cache`.

Dependencies:
- Uses NFSv4 rnodes, shared filehandles, filename reference helpers, vnode allocation/ops, rnode shadow-list lock, and the NFSv4 vnode ops table.

Notable details:
- Shadow vnodes have no pages; the master vnode owns cached file data and file resources.
- For non-regular files or root vnodes, shadowing is bypassed and the master shadow name can be refreshed after server-side renames.
- Creating a shadow vnode holds the master vnode until the shadow is inactivated.
